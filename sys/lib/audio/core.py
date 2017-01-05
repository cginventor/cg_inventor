import os
from cg_inventor.sys.utils import mime, encoding

LP_TYPE        = "lp"
EP_TYPE        = "ep"
COMP_TYPE      = "compilation"
LIVE_TYPE      = "live"
VARIOUS_TYPE   = "various"
DEMO_TYPE      = "demo"
SINGLE_TYPE    = "single"
ALBUM_TYPE_IDS = [LP_TYPE, EP_TYPE, COMP_TYPE, LIVE_TYPE, VARIOUS_TYPE, DEMO_TYPE, SINGLE_TYPE]

VARIOUS_ARTISTS = "Various Artists"

TXXX_ALBUM_TYPE    = "album_type"
TXXX_ARTIST_ORIGIN = "artist_origin"

#--------------------------------------------------------------------------------------------------#

AUDIO_NONE  = 0
AUDIO_MP3   = 1
AUDIO_TYPES = (AUDIO_NONE, AUDIO_MP3)

#--------------------------------------------------------------------------------------------------#

def load(path, tag_version=None):
    from . import mp3, id3; reload(mp3); reload(id3)
    
    if os.path.exists(path):
        if not os.path.isfile(path):
            raise IOError("Not a file: '%s'" %path)
    else:
        raise IOError("File not found: '%s'" %path)
    
    mime_type = mime.guessMimetype(path)
    mime_ext  = os.path.splitext(path)[1].lower()
    
    if (mime_type in mp3.MIME_TYPES) or (mime_ext in mp3.OTHER_MIME_TYPES):
        return mp3.Mp3AudioFile(path, tag_version)
      
    elif mime_type == id3.MIME_TYPE:
        return id3.TagFile(path, tag_version)

#--------------------------------------------------------------------------------------------------#

class AudioInfo():
    time_secs  = 0
    size_bytes = 0

#--------------------------------------------------------------------------------------------------#
    
class AudioFile():
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

    def _setArtist(self, val):
        raise NotImplementedError
    
    def _getArtist(self):
        raise NotImplementedError


    def _getAlbumArtist(self):
        raise NotImplementedError
    
    def _setAlbumArtist(self, val):
        raise NotImplementedError


    def _setAlbum(self, val):
        raise NotImplementedError
    
    def _getAlbum(self):
        raise NotImplementedError


    def _setTitle(self, val):
        raise NotImplementedError
    
    def _getTitle(self):
        raise NotImplementedError


    def _setTrackNum(self, val):
        raise NotImplementedError
    
    def _getTrackNum(self):
        raise NotImplementedError


    @property
    def artist(self):
        return self._getArtist()
    
    @artist.setter
    def artist(self, v):
        self._setArtist(v)


    @property
    def album_artist(self):
        return self._getAlbumArtist()
    
    @album_artist.setter
    def album_artist(self, v):
        self._setAlbumArtist(v)


    @property
    def album(self):
        return self._getAlbum()
    
    @album.setter
    def album(self, v):
        self._setAlbum(v)


    @property
    def title(self):
        return self._getTitle()
    
    @title.setter
    def title(self, v):
        self._setTitle(v)


    @property
    def track_num(self):
        return self._getTrackNum()
    
    @track_num.setter
    def track_num(self, v):
        self._setTrackNum(v)
            