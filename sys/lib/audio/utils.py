import os, re, math
import warnings, threading, logging

from cg_inventor.sys.utils.compat   import unicode, StringIO, python2
from cg_inventor.sys.utils.encoding import LOCAL_ENCODING, LOCAL_FS_ENCODING

#--------------------------------------------------------------------------------------------------#

def walk(handler, path, excludes=None, fs_encoding=LOCAL_FS_ENCODING):
    path = unicode(path, fs_encoding) if type(path) is not unicode else path

    excludes = excludes if excludes else []
    excludes_regex = []
    for exclude in excludes:
        excludes_regex.append(re.compile(exclude))

    def isExcluded(path):
        for regex in excludes_re:
            match = regex.match(path)
            if match: return True
        return False

    if not os.path.exists(path):
        raise IOError("file not found: %s" %path)
    
    elif os.path.isfile(path) and not isExcluded(path):
        handler.handleFile(os.path.abspath(path))
        return

    for root, dirs, files in os.walk(path):
        root = root if type(root) is unicode else unicode(root, fs_encoding)
        dirs.sort(); files.sort()
        
        for filename in files:
            filename = filename if type(filename) is unicode else unicode(filename, fs_encoding)
            filename = os.path.abspath(os.path.join(root, filename))
            
            if isExcluded(filename): continue
            
            try:
                handler.handleFile(f)
            except StopIteration:
                return

        if files:
            handler.handleDirectory(root, files)

#--------------------------------------------------------------------------------------------------#

class FileHandler(object):
    def handleFile(self, filepath):
        pass

    def handleDirectory(self, d, files):
        pass

    def handleDone(self):
        pass

#--------------------------------------------------------------------------------------------------#

def requireUnicode(*args):
    arg_indices = []
    kwarg_names = []
    for a in args:
        if type(a) is int:
            arg_indices.append(a)
        else:
            kwarg_names.append(a)
    assert(arg_indices or kwarg_names)

    def wrapper(fn):
        def wrapped_fn(*args, **kwargs):
            for index in arg_indices:
                if index >= len(args): break
                if args[index] is not None and not isinstance(args[index], unicode):
                    raise TypeError("%s(argument %d) must be unicode" %(fn.__name__, index))
                
            for name in kwarg_names:
                if name not in kwargs: continue
                if kwargs[name] is not None and not isinstance(kwargs[name], unicode):
                    raise TypeError("%s(argument %s) must be unicode" %(fn.__name__, name))
                
            return fn(*args, **kwargs)
        
        return wrapped_fn
    
    return wrapper


def encodeUnicode(replace=True):
    enc_err = "replace" if replace else "strict"

    if python2:
        def wrapper(fn):
            def wrapped_fn(*args, **kwargs):
                new_args = []
                for arg in args:
                    if type(arg) is unicode:
                        new_args.append(a.encode(LOCAL_ENCODING, enc_err))
                    else:
                        new_args.append(arg)
                args = tuple(new_args)

                for kwarg in kwargs:
                    if type(kwargs[kwarg]) is unicode:
                        kwargs[kwarg] = kwargs[kwarg].encode(LOCAL_ENCODING, enc_err)
                        
                return fn(*args, **kwargs)
            
            return wrapped_fn
        
        return wrapper
    
    else:
        def noop(fn):
            def call(*args, **kwargs):
                return fn(*args, **kwargs)
            
            return noop

#--------------------------------------------------------------------------------------------------#

def formatTime(seconds, total=None, short=False):
    def time_tuple(ts):
        if ts is None or ts < 0: ts = 0
        
        hours = ts / 3600
        mins  = (ts % 3600) / 60
        secs  = (ts % 3600) % 60
        tstr  = '%02d:%02d' %(mins, secs)
        if int(hours):
            tstr = '%02d:%s' %(hours, tstr)
            
        return (int(hours), int(mins), int(secs), tstr)

    if not short:
        hours, mins, secs, curr_str = time_tuple(seconds)
        retval = curr_str
        if total:
            hours, mins, secs, total_str = time_tuple(total)
            retval += ' / %s' %total_str
        return retval
    
    else:
        units = [(u'y', 60 * 60 * 24 * 7 * 52),
                 (u'w', 60 * 60 * 24 * 7),
                 (u'd', 60 * 60 * 24),
                 (u'h', 60 * 60),
                 (u'm', 60),
                 (u's', 1)]

        seconds = int(seconds)

        if seconds < 60:
            return u'   {0:02d}s'.format(seconds)
        
        for i in xrange(len(units) - 1):
            unit1, limit1 = units[i]
            unit2, limit2 = units[i + 1]
            if seconds >= limit1:
                return u'{0:02d}{1}{2:02d}{3}'.format(seconds // limit1, unit1, 
                                                    (seconds % limit1) // limit2, unit2)
            
        return u'  ~inf'

#--------------------------------------------------------------------------------------------------#

KB_BYTES = 1024
MB_BYTES = 1048576
GB_BYTES = 1073741824
KB_UNIT = "KB"
MB_UNIT = "MB"
GB_UNIT = "GB"


def formatSize(size, short=False):
    if not short:
        unit = "Bytes"
        if size >= GB_BYTES:
            size = float(size) / float(GB_BYTES)
            unit = GB_UNIT
        elif size >= MB_BYTES:
            size = float(size) / float(MB_BYTES)
            unit = MB_UNIT
        elif size >= KB_BYTES:
            size = float(size) / float(KB_BYTES)
            unit = KB_UNIT
            
        return "%.2f %s" % (size, unit)
    
    else:
        suffixes = u' kMGTPEH'
        if size == 0:
            num_scale = 0
        else:
            num_scale = int(math.floor(math.log(size) / math.log(1000)))
            
        if num_scale > 7:
            suffix = '?'
        else:
            suffix = suffixes[num_scale]
            
        num_scale = int(math.pow(1000, num_scale))
        str_value = str(size / num_scale)
        
        if len(str_value) >= 3 and str_value[2] == '.':
            str_value = str_value[:2]
        else:
            str_value = str_value[:3]
            
        return "{0:>3s}{1}".format(str_value, suffix)

#--------------------------------------------------------------------------------------------------#

def formatTimeDelta(time_delta):
    days = time_delta.days
    hours = time_delta.seconds / 3600
    mins = (time_delta.seconds % 3600) / 60
    secs = (time_delta.seconds % 3600) % 60
    
    time_str = "%02d:%02d:%02d" %(hours, mins, secs)
    if days:
        time_str = "%d days %s" %(days, time_str)
        
    return time_str

#--------------------------------------------------------------------------------------------------#

def chunkCopy(src_fp, dest_fp, chunk_sz=(1024 * 512)):
    done = False
    while not done:
        data = src_fp.read(chunk_sz)
        if data:
            dest_fp.write(data)
        else:
            done = True
        del data

#--------------------------------------------------------------------------------------------------#

def datePicker(thing, prefer_recording_date=False):
    if not prefer_recording_date:
        return (thing.original_release_date or
                thing.release_date or
                thing.recording_date)
    else:
        return (thing.recording_date or
                thing.original_release_date or
                thing.release_date)

#--------------------------------------------------------------------------------------------------#

def makeUniqueFileName(file_path, uniq=u''):
    path = os.path.dirname(file_path)
    file = os.path.basename(file_path)
    name, ext = os.path.splitext(file)
    count = 1
    
    while os.path.exists(os.path.join(path, file)):
        if uniq:
            name = "%s_%s" %(name, uniq)
            file = "%s%s" %(name, ext)
            uniq = u''
        else:
            name = "%s_%s" %(name, count)
            file = "%s%s" %(name, ext)
            count += 1
            
    return os.path.join(path, file)
