from .frames import Frame, TextFrame


class PCST(Frame):
    '''Indicates a podcast. The 4 bytes of data is undefined, and is typically all 0.'''
    
    def __init__(self, id="PCST"):
        super(PCST, self).__init__("PCST")


    def render(self):
        self.data = b"\x00" * 4
        return super(PCST, self).render()



class TKWD(TextFrame):
    '''Podcast keywords.'''

    def __init__(self, id="TKWD"):
        super(TKWD, self).__init__("TKWD")



class TDES(TextFrame):
    '''Podcast description. One encoding byte followed by text per encoding.'''

    def __init__(self, id="TDES"):
        super(TDES, self).__init__("TDES")



class TGID(TextFrame):
    '''Podcast URL of the audio file. This should be a W frame!'''

    def __init__(self, id="TGID"):
        super(TGID, self).__init__("TGID")



class WFED(TextFrame):
    '''Another podcast URL, the feed URL it is said.'''

    def __init__(self, id="WFED", url=""):
        super(WFED, self).__init__("WFED", unicode(url))
