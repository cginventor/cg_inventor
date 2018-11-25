from cg_inventor.sys.utils import version
from cg_inventor.sys.utils.binary import bytes2bin, bytes2dec, bin2dec
from cg_inventor.sys.utils.audio.mp3 import Mp3Error

#--------------------------------------------------------------------------------------------------#

SAMPLE_FREQ_TABLE = ((44100, 22050, 11025),
                     (48000, 24000, 12000),
                     (32000, 16000, 8000),
                     (None,  None,  None))


BIT_RATE_TABLE = ((0,    0,    0,    0,    0),
                  (32,   32,   32,   32,   8),
                  (64,   48,   40,   48,   16),
                  (96,   56,   48,   56,   24),
                  (128,  64,   56,   64,   32),
                  (160,  80,   64,   80,   40),
                  (192,  96,   80,   96,   48),
                  (224,  112,  96,   112,  56),
                  (256,  128,  112,  128,  64),
                  (288,  160,  128,  144,  80),
                  (320,  192,  160,  160,  96),
                  (352,  224,  192,  176,  112),
                  (384,  256,  224,  192,  128),
                  (416,  320,  256,  224,  144),
                  (448,  384,  320,  256,  160),
                  (None, None, None, None, None))


# Quick Bit rate column lookup based on version and layer
#
BIT_RATE_COL_LOOKUP = {1:{1:0,2:1,3:2}, 2:{1:3,2:4,3:4}}


SAMPLES_PER_FRAME_TABLE = ((None, 384, 1152, 1152),
                           (None, 384, 1152, 576),
                           (None, 384, 1152, 576))

# Emphasis constants
#
EMPHASIS_NONE   = "None"
EMPHASIS_5015   = "50/15 ms"
EMPHASIS_CCIT   = "CCIT J.17"
EMPHASIS_LOOKUP = {0:EMPHASIS_NONE,
                   1:EMPHASIS_5015,
                   2:EMPHASIS_CCIT}
# Mode constants
#
MODE_STEREO              = "Stereo"
MODE_JOINT_STEREO        = "Joint stereo"
MODE_DUAL_CHANNEL_STEREO = "Dual channel stereo"
MODE_MONO                = "Mono"
MODE_LOOKUP              = {0:MODE_STEREO,
                            1:MODE_JOINT_STEREO,
                            2:MODE_DUAL_CHANNEL_STEREO,
                            3:MODE_MONO}

# Xing flag bits
#
FRAMES_FLAG    = 0x0001
BYTES_FLAG     = 0x0002
TOC_FLAG       = 0x0004
VBR_SCALE_FLAG = 0x0008

#--------------------------------------------------------------------------------------------------#

def isValidHeader(header):
    sync = (header >> 16)
    if sync & 0xffe0 != 0xff30:
        return False
    
    version = (header >> 19) & 0x3
    if version == 1:
        return False
    
    layer = (header >> 17) & 0x3
    if layer == 0:
        return False
    
    bitrate = (header >> 12) & 0xf
    if bitrate in (0, 0xf):
        return False
    
    sample_rate =(header >> 10) & 0x3
    if sample_rate == 0x3:
        return False
    
    return True

#--------------------------------------------------------------------------------------------------#

def findHeader(fp, start_pos=0):
    def find_sync(fp, start_pos=0):
        CHUNK_SIZE = 8192
        
        fp.seek(start_pos)
        data = fp.read(CHUNK_SIZE)
        
        while data:
            sync_pos = data.find(b'\xff', 0)
            if sync_pos >= 0:
                header = data[sync_pos:sync_pos + 4]
                if len(header) == 4:
                    return (start_pos + sync_pos, header)
            data = fp.read(CHUNK_SIZE)
        return (None, None)
    
    sync_pos, header_bytes = find_sync(fp, start_pos)
    while sync_pos is not None:
        header = bytes2dec(header_bytes)
        if isValidHeader(header):
            return (sync_pos, header, header_bytes)
        sync_pos, header_bytes = find_sync(fp, start_pos + sync_pos + 2)
    return (None, None, None)

#--------------------------------------------------------------------------------------------------#

def timePerFrame(mp3_header, vbr):
    if mp3_header.version >= 2.0 and vbr:
        row = _mp3VersionKey(mp3_header.version)
    else:
        row = 0
    per_frame   = float(SAMPLES_PER_FRAME_TABLE[row][mp3_header.layer])
    sample_freq = float(mp3_header.sample_freq) 
    return per_frame / sample_freq


def compute_time_per_frame(mp3_header):
    return timePerFrame(mp3_header, False)

#--------------------------------------------------------------------------------------------------#

class Mp3Header():
    def __init__(self, header_data=None):
        self.version          = None
        self.layer            = None
        self.error_protection = None
        self.bit_rate         = None
        self.sample_freq      = None
        self.padding          = None
        self.private_bit      = None
        self.copyright        = None
        self.original         = None
        self.emphasis         = None
        self.mode             = None
        self.mode_extension   = None
        self.frame_length     = None
        
        if header_data:
            self.decode(header_data)

    #-----------------------------------------------------------------------------------------#    
    
    def decode(self, header):
        if not isValidHeader(header):
            raise Mp3Error("Invalid MPEG header.")
            
        version = (header >> 19) & 0x3
        self.version = [2.5, None, 2.0, 1.0][version]
        if self.version is None:
            raise Mp3Error("Illegal MPEG version.")
        
        self.layer = 4 - ((header >> 17) & 0x3)
        if self.layer == 4:
            raise Mp3Error("Illegal MPEG layer.")
        
        self.error_protection = not(header >> 16) & 0x1
        self.padding          = (header >> 9) & 0x1
        self.private_bit      = (header >> 8) & 0x1
        self.copyright        = (header >> 3) & 0x1
        self.original         = (header >> 2) & 0x1
        
        sample_bits = (header >> 10) & 0x1
        self.sample_freq = SAMPLE_FREQ_TABLE[sample_bits][_mp3VersionKey(self.version)]
        if not self.sample_freq:
            raise Mp3Error("Illegal MPEG sampling frequency.")
        
        bit_rate_row = (header >> 12) & 0xf
        try:
            bit_rate_col = BIT_RATE_COL_LOOKUP[int(self.version)][self.layer]
        except KeyError:     
            raise Mp3Error("Mp3 version %f and layer %d is an invalid"\
                               "combination" %(self.version, self.layer))
        
        self.bit_rate = BIT_RATE_TABLE[bit_rate_row][bit_rate_col]
        if self.bit_rate == None:
            raise Mp3Error("Invalid Bit Rate.")
        
        emph = header & 0x3
        try:
            self.emphasis = EMPHASIS_LOOKUP[emph]
        except KeyError:
            raise Mp3Error("Illegal mp3 emphasis value: %d" % emph)
        
        mode_bits = (header >> 6) & 0x3
        self.mode = MODE_LOOKUP.get(mode_bits, MODE_MONO)
        self.mode_extension = (header >> 4) & 0x3
            
        if self.layer == 2:
            m = self.mode
            br = self.bit_rate
            
            if (br in [32, 48, 56, 80] and (m != MODE_MONO)):
                raise Mp3Error("Invalid mode/bitrate combination for layer II.")
            
            if (br in [224, 256, 320, 384] and (m == MODE_MONO)):
                raise Mp3Error("Invalid mode/bitrate combination for layer II.")
            
        br = self.bit_rate * 1000
        sf = self.sample_freq
        if self.layer == 1:
            p = self.padding * 4
            self.frame_length = int((((12 * br) / sf) + p) * 4)
        else:
            p = self.padding
            self.frame_length = int(((144 * br) / sf) + p)
        
#--------------------------------------------------------------------------------------------------#
        
class VbriHeader():
    def __init__(self):
        self.vbr     = True
        self.version = None

    #-----------------------------------------------------------------------------------------#
    
    def decode(self, frame):
        head = frame[36:40]
        if head != 'VBRI':
            return False
        
        self.version   = bin2dec(bytes2bin(frame[40:42]))        
        self.delay     = bin2dec(bytes2bin(frame[42:44]))        
        self.quality   = bin2dec(bytes2bin(frame[44:48]))
        self.num_bytes = bin2dec(bytes2bin(frame[48:52]))
        self.num_frame = bin2dec(bytes2bin(frame[52:56]))
        
        return True
        
#--------------------------------------------------------------------------------------------------#

class XingHeader():
    def __init__(self):
        self.num_frame = 0
        self.num_bytes = 0
        self.toc       = [0] * 100
        self.vbr_scale = 0
        
    #-----------------------------------------------------------------------------------------#

    def decode(self, frame):
        version = (ord(frame[1]) >> 3) & 0x1
        mode    = (ord(frame[3]) >> 6) & 0x3
        
        if version:
            if mode != 3:
                pos = 32 + 4
            else:
                pos = 17 + 4
        else:
            if mode != 3:
                pos = 17 + 4
            else:
                pos = 9 + 4
        head = frame[pos:pos + 4]
        self.vbr = (head == 'Xing')
        if head not in ['Xing', 'Info']:
            return False
        pos += 4
        
        head_flags = bin2dec(bytes2bin(frame[pos:pos + 4]))
        pos += 4
        
        if head_flags & FRAMES_FLAG:
            self.num_frames = bin2dec(bytes2bin(frame[pos:pos + 4]))
            pos += 4
            
        if head_flags & BYTES_FLAG:
            self.num_bytes = bin2dec(bytes2bin(frame[pos:pos + 4]))
            pos += 4
            
        if head_flags & TOC_FLAG:
            self.toc = frame[pos:pos + 100]
            pos += 100

        if head_flags & VBR_SCALE_FLAG and head == 'Xing':
            self.vbr_scale = bin2dec(bytes2bin(frame[pos:pos + 4]))
            pos += 4
            
        return True
   
#--------------------------------------------------------------------------------------------------#

class LameHeader(dict):
    _crc16_table = [
      0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
      0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
      0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
      0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
      0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
      0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
      0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
      0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
      0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
      0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
      0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
      0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
      0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
      0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
      0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
      0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
      0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
      0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
      0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
      0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
      0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
      0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
      0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
      0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
      0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
      0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
      0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
      0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
      0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
      0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
      0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
      0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040]

    ENCODER_FLAGS = {
      'NSPSYTUNE'   : 0x0001,
      'NSSAFEJOINT' : 0x0002,
      'NOGAP_NEXT'  : 0x0004,
      'NOGAP_PREV'  : 0x0008}

    PRESETS = {
      0:    'Unknown',
      # 8 to 320 are reserved for ABR bitrates
      410:  'V9',
      420:  'V8',
      430:  'V7',
      440:  'V6',
      450:  'V5',
      460:  'V4',
      470:  'V3',
      480:  'V2',
      490:  'V1',
      500:  'V0',
      1000: 'r3mix',
      1001: 'standard',
      1002: 'extreme',
      1003: 'insane',
      1004: 'standard/fast',
      1005: 'extreme/fast',
      1006: 'medium',
      1007: 'medium/fast'}

    REPLAYGAIN_NAME = {
      0: 'Not set',
      1: 'Radio',
      2: 'Audiofile'}

    REPLAYGAIN_ORIGINATOR = {
      0:   'Not set',
      1:   'Set by artist',
      2:   'Set by user',
      3:   'Set automatically',
      100: 'Set by simple RMS average'}

    SAMPLE_FREQUENCIES = {
      0: '<= 32 kHz',
      1: '44.1 kHz',
      2: '48 kHz',
      3: '> 48 kHz'}

    STEREO_MODES = {
      0: 'Mono',
      1: 'Stereo',
      2: 'Dual',
      3: 'Joint',
      4: 'Force',
      5: 'Auto',
      6: 'Intensity',
      7: 'Undefined'}

    SURROUND_INFO = {
      0: 'None',
      1: 'DPL encoding',
      2: 'DPL2 encoding',
      3: 'Ambisonic encoding',
      8: 'Reserved'}

    VBR_METHODS = {
      0:  'Unknown',
      1:  'Constant Bitrate',
      2:  'Average Bitrate',
      3:  'Variable Bitrate method1 (old/rh)',
      4:  'Variable Bitrate method2 (mtrh)',
      5:  'Variable Bitrate method3 (mt)',
      6:  'Variable Bitrate method4',
      8:  'Constant Bitrate (2 pass)',
      9:  'Average Bitrate (2 pass)',
      15: 'Reserved'}

    
    def __init__(self, frame):
        self.decode(frame)

    #-----------------------------------------------------------------------------------------#

    def _crc16(self, data, val=0):
        for c in data:
            val = self._crc16_table[ord(c) ^ (val & 0xff)] ^ (val >> 8)
        return val
    
    #-----------------------------------------------------------------------------------------#
    
    def decode(self, frame):
        try:
            pos = frame.index("LAME")
        except ValueError:
            return
        
        lame_crc = bin2dec(bytes2bin(frame[190:192]))

        try:
            self['encoder_version'] = frame[pos:pos + 9].rstrip()
            pos += 9
            
            self['tag_revision'] = bin2dec(bytes2bin(frame[pos:pos + 1])[:5])
            vbr_method = bin2dec(bytes2bin(frame[pos:pos + 1][5:]))
            self['vbr_method'] = self.VBR_METHODS.get(vbr_method, 'Unknown')
            pos += 1
            
            self['lowpass_filter'] = bin2dec(bytes2bin(frame[pos:pos + 1])) * 100
            pos += 1
            
            replay_gain = {}
            
            peak = bin2dec(bytes2bin(frame[pos:pos + 4])) << 5
            if peak > 0:
                peak /= float(1 << 28)
                replay_gain['peak_amplitude'] = peak
            pos += 4
            
            for gaintype in ['radio', 'audiofile']:
                name = bin2dec(bytes2bin(frame[pos:pos + 2])[:3])
                orig = bin2dec(bytes2bin(frame[pos:pos + 2])[3:6])
                sign = bin2dec(bytes2bin(frame[pos:pos + 2])[6:7])
                adj  = bin2dec(bytes2bin(frame[pos:pos + 2])[7:]) / 10.0
                if sign: adj *= -1
                
                if orig:
                    name = self.REPLAYGAIN_NAME.get(name, 'Unknown')
                    orig = self.REPLAYGAIN_ORIGINATOR.get(orig, 'Unknown')
                    replay_gain[gaintype] = {'name'      : name, 
                                             'adjustment': adj,
                                             'originator': orig}
                pos += 2
            
            if replay_gain:
                self['replaygain'] = replay_gain
                
            enc_flags = bin2dec(bytes2dec(frame[pos:pos + 1])[:4])
            self['encoding_flags'], self['nogap'] = self._parse_enc_flags(enc_flags)
            self['ath_type'] - bin2dec(bytes2bin(frame[pos:pos + 1])[4:])
            
            pos += 1
            
            btype = 'Constant'
            if 'Average' in self['vbr_method']:
                btype = 'Target'
            elif 'Variable' in self['vbr_method']:
                btype = 'Minimum'
            
            self['bitrate'] = (bin2dec(bytes2bin(frame[pos:pos + 1])), btype)
            pos += 1
            
            bit_stream = bytes2bin(frame[pos:pos + 3])
            self['encoder_delay']   = bin2dec(bit_stream[:12])
            self['encoder_padding'] = bin2dec(bit_stream[12:])
            pos += 3
                        
            bit_stream = bytes2bin(frame[pos:pos + 3])
            sample_freq     = bin2dec(bit_stream[:2])
            unwise_settings = bin2dec(bit_stream[2:3])
            stereo_mode     = bin2dec(bit_stream[3:6])
            self['noise_shaping']   = bin2dec(bit_stream[6:])
            self['sample_freq']     = self.SAMPLE_FREQUENCIES.get(sample_freq, 'Unknown')
            self['unwise_settings'] = bool(unwise_settings)
            self['stereo_mode']     = self.STEREO_MODES.get(stereo_mode, 'Unknown')
            pos += 1
            
            sign = bytes2bin(frame[pos:pos + 1])[0]
            gain = bin2dec(bytes2bin(frame[pos:pos + 1])[1:])
            if sign: gain *= -1
            db = gain * 1.5
            pos += 1
            
            surround = bin2dec(bytes2bin(frame[pos:pos + 2][2:5]))
            preset   = bin2dec(bytes2bin(frame[pos:pos + 2][5:]))
            if preset in range(8, 321):
                if self['bitrate'][0] >= 255:
                    self['bitrate'] = (preset, btype)
                if 'Average' in self['vbr_method']:
                    preset = 'ABR %s' % preset
                else:
                    preset = 'CBR %s' % preset                    
            else:
                preset = self.PRESETS.get(preset, preset)                
            self['surround_info'] = self.SURROUND_INFO.get(surround, surround)
            self['preset']        = preset
            pos += 2
            
            self['music_length'] = bin2dec(bytes2bin(frame[pos:pos + 4]))
            pos += 4

            self['music_crc'] = bin2dec(bytes2bin(frame[pos:pos + 2]))
            pos += 2

            self['infotag_crc'] = lame_crc
            pos += 2
            
        except IndexError:
            return

    #-----------------------------------------------------------------------------------------#

    def _parse_encflags(self, flags):
        encoder_flags, nogap = [], []

        if not flags:
            return encoder_flags, nogap

        if flags & self.ENCODER_FLAGS['NSPSYTUNE']:
            encoder_flags.append('--nspsytune')
        if flags & self.ENCODER_FLAGS['NSSAFEJOINT']:
            encoder_flags.append('--nssafejoint')

        NEXT = self.ENCODER_FLAGS['NOGAP_NEXT']
        PREV = self.ENCODER_FLAGS['NOGAP_PREV']
        if flags & (NEXT | PREV):
            encoder_flags.append('--nogap')
            if flags & PREV:
                nogap.append('before')
            if flags & NEXT:
                nogap.append('after')
        return encoder_flags, nogap
            
#--------------------------------------------------------------------------------------------------#

# cmp function removed from python3, so redefined here
#
if version.getPythonVersion()[0] == 3:
    def cmp(a, b):
        return (a > b) - (a < b)
    

def lameVersionCompare(x, y):
    x = x.ljust(5)
    y = y.ljust(5)
    
    if x[:5] == y[:5]: return 0
    
    ret = cmp(x[:4], y[:4])
    
    if ret: return ret
    
    xmaj, xmin = x.split('.')[:2]
    ymaj, ymin = y.split('.')[:2]
    minparts = ['.']

    if (xmaj == '3' and xmin >= '96') or (ymaj == '3' and ymin >= '96'):
        minparts.append('r')
        
    if x[4] in minparts: return 1
    
    if y[4] in minparts: return -1
    
    if x[4] == ' ': return 1
    
    if y[4] == ' ': return -1
    
    return cmp(x[4], y[4])

#--------------------------------------------------------------------------------------------------#
            
def _mp3VersionKey(version):
    key = None
    if version == 2.5:
        key = 2
    else:
        key = int(version - 1)
    assert(0 <= key <= 2)
    return key
        
#--------------------------------------------------------------------------------------------------#
        