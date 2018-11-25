import os, re
from cg_inventor.sys.utils.video import core

NAME = "mpeg"

MIME_TYPES = ["video/mpeg", 
              "video/mp4", 
              "video/x-m4v"
              "video/x-mpeg"]

OTHER_MIME_TYPES = []

EXTENSIONS = ['.mp4','mpe','.mpeg','.mpg', '.m1v', '.m2v', '.mp2', '.mp3', '.mpa','.mpga']

#--------------------------------------------------------------------------------------------------#

def isMpegFile(file_name):
    return core.guessMimetype(file_name) in MIME_TYPES

#--------------------------------------------------------------------------------------------------#

class MpegError(Exception):
    pass

#--------------------------------------------------------------------------------------------------#

class Mp3AudioInfo(core.AudioInfo):
    def __init__(self, file_obj, start_offset, tag):
        from cg_inventor.sys.utils.video import headers
        
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