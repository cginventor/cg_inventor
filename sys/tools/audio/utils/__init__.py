from cg_inventor.sys.utils.encoding import LOCAL_FS_ENCODING
import os, re

def walk(handler, path, excludes=None, fs_encoding=LOCAL_FS_ENCODING):
    path = unicode(path, fs_encoding) if type(path) is not unicode else path

    excludes = excludes if excludes else []
    excludes_re = []
    for e in excludes:
        excludes_re.append(re.compile(e))

    def _isExcluded(_p):
        for ex in excludes_re:
            match = ex.match(_p)
            if match:
                return True
        return False

    if not os.path.exists(path):
        raise IOError("file not found: %s" % path)
    elif os.path.isfile(path) and not _isExcluded(path):
        handler.handleFile(os.path.abspath(path))
        return

    for (root, dirs, files) in os.walk(path):
        root = root if type(root) is unicode else unicode(root, fs_encoding)
        dirs.sort()
        files.sort()
        for f in files:
            f = f if type(f) is unicode else unicode(f, fs_encoding)
            f = os.path.abspath(os.path.join(root, f))
            if not _isExcluded(f):
                try:
                    handler.handleFile(f)
                except StopIteration:
                    return

        if files:
            handler.handleDirectory(root, files)