import os, mimetypes, time

from cg_inventor.sys.utils import version
from cg_inventor.sys.utils import encoding

#--------------------------------------------------------------------------------------------------#

ID3_MIME_TYPE            = "application/x-id3"
ID3_MIME_TYPE_EXTENSIONS = (".id3", ".tag")

if version.getPythonVersion()[0] == 2:
    from StringIO import StringIO        
else:
    from io import StringIO

mime_types = mimetypes.MimeTypes()
mime_str = "%s %s" %(ID3_MIME_TYPE, " ".join([ext[1:] for ext in ID3_MIME_TYPE_EXTENSIONS]))
mime_types.readfp(StringIO(mime_str))

del mimetypes
del StringIO

#--------------------------------------------------------------------------------------------------#

def guessMimetype(file_name, with_encoding=False):
    mime, enc = mime_types.guess_type(file_name, strict=False)
    return mime if not with_encoding else (mime, enc)

#--------------------------------------------------------------------------------------------------#

def load(path, tag_version=None):
    from cg_inventor.sys.utils.video import mpeg, avi
    
    if os.path.exists(path):
        if not os.path.isfile(path):
            raise IOError("Not a file: '%s'" %path)
    else:
        raise IOError("File not found: '%s'" %path)
    
    mime_type = guessMimetype(path)
    mime_ext  = os.path.splitext(path)[1].lower()
    
    print mime_type, mime_ext
    
    if (mime_type in mpeg.MIME_TYPES) or (mime_ext in mpeg.OTHER_MIME_TYPES):
        print 'MPEG'
        return mpeg.MpegVideoFile(path, tag_version)
    
    if (mime_type in avi.MIME_TYPES) or (mime_ext in avi.OTHER_MIME_TYPES):
        print 'AVI'
        return mpeg.AviVideoFile(path, tag_version)
          
    elif mime_type == ID3_MIME_TYPE:
        return id3.TagFile(path, tag_version)
    
    else:
        return None
    
#--------------------------------------------------------------------------------------------------#
    
VIDEO_NONE  = 0
VIDEO_AVI   = 1
VIDEO_MPG   = 2
VIDEO_TYPES = (VIDEO_NONE, VIDEO_AVI, VIDEO_MPG)

#--------------------------------------------------------------------------------------------------#

class VideoInfo():
    time_secs  = 0
    size_bytes = 0
    resolution = None

#--------------------------------------------------------------------------------------------------#
    
class VideoFile():
    def __init__(self, path):
        self.path = path
        self.type = None
        self._info = None
        self._tag  = None
        self._read()
        
    #------------------------------------------------------------------------------------------#    
    
    def _read(self):
        raise NotImplementedError()
    
    #------------------------------------------------------------------------------------------#       
    
    def rename(self, name, 
                     fsencoding         = encoding.LOCAL_FS_ENCODING, 
                     preserve_file_time = False):
        base     = os.path.basename(self.path)
        base_ext = os.path.splitext(base)[1]
        dir      = os.path.dirname(self.path)
        if not dir: dir = '.'
        
        new_name = "%s%s" %(os.path.join(dir, name), base_ext)
        if os.path.exists(new_name):
            raise IOError("File '%s' already exists. Cannot overwrite." %new_name)
        elif not os.path.exists(os.path.dirname(new_name)):
            dir_name = os.path.dirname(new_name)
            raise IOError("Target Directory '%s' does not exist. Cannot create." %dir_name)
        
        os.rename(self.path, new_name)
        self.tag.file_info.name = new_name
        self.path = new_name
        
        if not preserve_file_time: return
        
        self.tag.file_info.touch((self.tag.file_info.atime,
                                  self.tag.file_info.mtime))
    
    #------------------------------------------------------------------------------------------#        
        
    @property
    def path(self):
        return self._path
    
    @path.setter
    def path(self, path):
        from os.path import abspath, realpath, normpath
        self._path = normpath(realpath(abspath(path)))
        
        
    @property
    def info(self):
        return self._info
    

    @property
    def tag(self):
        return self._tag
    
    @tag.setter
    def tag(self, tag):
        self._tag = tag


#--------------------------------------------------------------------------------------------------#

class Tag(object):
    read_only = False

    def _setTitle(self, val):
        raise NotImplementedError
    
    def _getTitle(self):
        raise NotImplementedError


    def _getAuthor(self):
        raise NotImplementedError
    
    def _setAuthor(self, val):
        raise NotImplementedError


    def _setCopyright(self, val):
        raise NotImplementedError
    
    def _getCopyright(self):
        raise NotImplementedError


    def _setDescription(self, val):
        raise NotImplementedError
    
    def _getDescription(self):
        raise NotImplementedError


    def _setRating(self, val):
        raise NotImplementedError
    
    def _getRating(self):
        raise NotImplementedError
    
    
    @property
    def title(self):
        return self._getArtist()
    
    @title.setter
    def title(self, v):
        self._setArtist(v)


    @property
    def author(self):
        return self._getAlbumArtist()
    
    @author.setter
    def author(self, v):
        self._setAlbumArtist(v)


    @property
    def copyright(self):
        return self._getAlbum()
    
    @copyright.setter
    def copyright(self, v):
        self._setAlbum(v)


    @property
    def description(self):
        return self._getTitle()
    
    @description.setter
    def description(self, v):
        self._setTitle(v)


    @property
    def rating(self):
        return self._getTrackNum()
    
    @rating.setter
    def rating(self, v):
        self._setTrackNum(v)
        
#--------------------------------------------------------------------------------------------------#

class Date():
    TIME_STAMP_FORMATS = ["%Y",
                          "%Y-%m",
                          "%Y-%m-%d",
                          "%Y-%m-%dT%H",
                          "%Y-%m-%dT%H:%M",
                          "%Y-%m-%dT%H:%M:%S",
                          "%Y-%m-%dT%HZ",
                          "%Y-%m-%dT%H:%MZ",
                          "%Y-%m-%dT%H:%M:%SZ",
                          "%Y-%m-%d %H:%M:%S",
                          "%Y-00-00"]

    def __init__(self, year, month=None, day=None, hour=None, minute=None, second=None):
        from datetime import datetime
        datetime(year, 
                 month  if month  is not None else 1,
                 day    if day    is not None else 1,
                 hour   if hour   is not None else 0,
                 minute if minute is not None else 0,
                 second if second is not None else 0)

        self._year   = year
        self._month  = month
        self._day    = day
        self._hour   = hour
        self._minute = minute
        self._second = second

        Date._validateFormat(str(self))
        
    #------------------------------------------------------------------------------------------#  

    @property
    def year(self):
        return self._year
    
    @property
    def month(self):
        return self._month
    
    @property
    def day(self):
        return self._day
    
    @property
    def hour(self):
        return self._hour
    
    @property
    def minute(self):
        return self._minute
    
    @property
    def second(self):
        return self._second
    
    #------------------------------------------------------------------------------------------#  

    def __eq__(self, rhs):
        if not rhs:
            return False

        return (self.year   == rhs.year   and
                self.month  == rhs.month  and
                self.day    == rhs.day    and
                self.hour   == rhs.hour   and
                self.minute == rhs.minute and
                self.second == rhs.second)

    def __ne__(self, rhs):
        return not(self == rhs)

    def __lt__(self, rhs):
        if not rhs:
            return True

        for l, r in ((self.year,   rhs.year),
                     (self.month,  rhs.month),
                     (self.day,    rhs.day),
                     (self.hour,   rhs.hour),
                     (self.minute, rhs.minute),
                     (self.second, rhs.second)):
            if l < r:
                return True
            elif l > r:
                return False
        return False

    def __hash__(self):
        return hash(str(self))

    #------------------------------------------------------------------------------------------#  

    @staticmethod
    def _validateFormat(date_str):
        pdate = None
        for date_format in Date.TIME_STAMP_FORMATS:
            try:
                pdate = time.strptime(date_str, date_format)
                break
            except ValueError:
                continue

        if pdate is None:
            raise ValueError("Invalid date string: %s." %date_str)

        assert(pdate)
        return pdate, date_format


    @staticmethod
    def parse(date_str):
        date_str = date_str.strip('\x00')

        pdate, date_format = Date._validateFormat(date_str)

        kwargs = {}
        if "%m" in date_format:
            kwargs["month"]  = pdate.tm_mon
        if "%d" in date_format:
            kwargs["day"]    = pdate.tm_mday
        if "%H" in date_format:
            kwargs["hour"]   = pdate.tm_hour
        if "%M" in date_format:
            kwargs["minute"] = pdate.tm_min
        if "%S" in date_format:
            kwargs["second"] = pdate.tm_sec

        return Date(pdate.tm_year, **kwargs)
    
    #------------------------------------------------------------------------------------------#  

    def __str__(self):
        date_str = "%d" %self.year
        if self.month:
            date_str += "-%s" %str(self.month).rjust(2, '0')
            if self.day:
                date_str += "-%s" %str(self.day).rjust(2, '0')
                if self.hour is not None:
                    date_str += "T%s" %str(self.hour).rjust(2, '0')
                    if self.minute is not None:
                        date_str += ":%s" %str(self.minute).rjust(2, '0')
                        if self.second is not None:
                            date_str += ":%s" %str(self.second).rjust(2, '0')
        return date_str


    