import os, re
from cg_inventor.sys.utils.audio import core, id3

NAME = "mpeg"

MIME_TYPES = ["audio/mpeg", 
              "audio/mp3", 
              "audio/x-mp3", 
              "audio/x-mpeg",
              "audio/mpeg3", 
              "audio/x-mpeg3", 
              "audio/mpg", 
              "audio/x-mpg",
              "audio/x-mpegaudio"]

OTHER_MIME_TYPES = ['application/octet-stream',
                    'audio/x-hx-aac-adts',
                    'audio/x-wav']

EXTENSIONS = ['.mp3', '.m2a', '.mpg', '.mpga', '.mp2', '.mpa']

#--------------------------------------------------------------------------------------------------#

def isMp3File(file_name):
    return core.guessMimetype(file_name) in MIME_TYPES

#--------------------------------------------------------------------------------------------------#

class Mp3Error(Exception):
    pass

#--------------------------------------------------------------------------------------------------#

class Mp3AudioInfo(core.AudioInfo):
    def __init__(self, file_obj, start_offset, tag):
        from cg_inventor.sys.utils.audio import headers
        
        core.AudioInfo.__init__(self)        
        
        self.mp3_header  = None
        self.xing_header = None
        self.vbri_header = None
        self.lame_tag    = None
        self.bit_rate    = (None, None)
        
        while self.mp3_header is None:
            (header_pos, header_int, header_bytes) = headers.findHeader(file_obj, start_offset)
            if not header_int:
                raise Mp3Error("Unable to find a valid mp3 frame.")
        
            try:
                self.mp3_header = headers.Mp3Header(header_int)
            except headers.Mp3Error:
                start_offset += 4
                
        file_obj.seek(header_pos)
        mp3_frame = file_obj.read(self.mp3_header.frame_length)
        if re.compile(b'Xing|Info').search(mp3_frame):
            self.xing_header = headers.XingHeader()
            if not self.xing_header.decode(mp3_frame):
                self.xing_header = None
        elif mp3_frame.find(b'VBRI') >= 0:
            self.vbri_header = headers.VbriHeader()
            if not self.vbri_header.decode(mp3_frame):
                self.vbri_header = None
        
        self.lame_tag = headers.LameHeader(mp3_frame)
        
        import stat
        self.size_bytes = os.stat(file_obj.name)[stat.ST_SIZE]
        
        time_per_frame = None
        if self.xing_header and self.xing_header.vbr:
            time_per_frame = headers.timePerFrame(self.mp3_header, True)
            self.time_secs = int(time_per_frame * self.xing_header.num_frames)
        elif self.vbri_header and self.vbri_header.version == 1:
            time_per_frame = headers.timePerFrame(self.mp3_header, True)
            self.time_secs = int(time_per_frame * self.vbri_header.num_frames)
        else:
            time_per_frame = headers.timePerFrame(self.mp3_header, False)
            length = self.size_bytes
            if tag and tag.isV2():
                length -= tag.header.SIZE + tag.header.tag_size
                file_obj.seek(-128, 2)
                if file_obj.read(3) == "TAG":
                    length -= 128
            elif tag and tag.isV1():
                length -= 128
            self.time_secs = int((length / self.mp3_header.frame_length) * time_per_frame)
            
        if (self.xing_header and self.xing_header.vbr and self.xing_header.num_frames):
            bit_rate = int((self.xing_header.num_bytes * 8) /
                      (time_per_frame * self.xing_header.num_frames * 1000))
            vbr = True
        else:
            bit_rate = self.mp3_header.bit_rate
            vbr = False
        self.bit_rate = (vbr, bit_rate)

        self.sample_freq = self.mp3_header.sample_freq
        self.mode        = self.mp3_header.mode

    #------------------------------------------------------------------------------------------#    
        
    @property
    def bit_rate_str(self):
        vbr, bit_rate = self.bit_rate
        bit_rate_str = "%d kb/s" %bit_rate
        if vbr:
            bit_rate_str = "~" + bit_rate_str
        return bit_rate_str
            
#--------------------------------------------------------------------------------------------------#

class Mp3AudioFile(core.AudioFile):
    def __init__(self, path, version=id3.ID3_ANY_VERSION):
        self._tag_version = version
        
        core.AudioFile.__init__(self, path)
        assert(self.type == core.AUDIO_MP3)

    #------------------------------------------------------------------------------------------#    
    
    def _read(self):
        with open(self.path, 'rb') as file_obj:
            self._tag = id3.Tag()
            tag_found = self._tag.parse(file_obj, self._tag_version)
            
            if tag_found and self._tag.isV1():
                mp3_offset = 0
            elif tag_found and self._tag.isV2():
                mp3_offset = self._tag_header.SIZE + self._tag.header.tag_size
            else:
                mp3_offset = 0
                self._tag = None
                
            try:
                self._info = Mp3AudioInfo(file_obj, mp3_offset, self._tag)
            except Mp3Error:
                self._info = None
            
            self.type = core.AUDIO_MP3
            
    #------------------------------------------------------------------------------------------#    
            
    def initTag(self, version=core.ID3_DEFAULT_VERSION):
        self.tag = id3.Tag()
        self.tag.version = version
        self.tag.file_info = id3.FileInfo(self.path)
        