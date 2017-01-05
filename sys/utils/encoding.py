import sys, locale 

DEFAULT_ENCODING = 'latin1'

LOCAL_ENCODING = locale.getpreferredencoding(do_setlocale=True)
if not LOCAL_ENCODING or LOCAL_ENCODING == "ANSI_X3.4-1968":
    LOCAL_ENCODING = DEFAULT_ENCODING
    
LOCAL_FS_ENCODING = sys.getfilesystemencoding()
if not LOCAL_FS_ENCODING:
    LOCAL_FS_ENCODING = DEFAULT_ENCODING
    
