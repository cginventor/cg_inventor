import re
from StringIO import StringIO

from cg_inventor.sys.utils import mime

from .. import core

#--------------------------------------------------------------------------------------------------#

MIME_TYPE  = "application/x-id3"

EXTENSIONS = (".id3", ".tag")

mime_str = "%s %s" %(MIME_TYPE, " ".join([ext[1:] for ext in EXTENSIONS]))
mime.mime_types.readfp(StringIO(mime_str))

#--------------------------------------------------------------------------------------------------#

V1              = (1, None, None)
V1_0            = (1, 0, 0)
V1_1            = (1, 1, 0)
V2              = (2, None, None)
V2_2            = (2, 2, 0)
V2_3            = (2, 3, 0)
V2_4            = (2, 4, 0)
DEFAULT_VERSION = V2_4
ANY_VERSION     = (V1[0] | V2[0], None, None)

VERSION_LOOKUP = {V1_0:"v1.0", V1_1:"v1.1", V1  :"v1.x",
                  V2_2:"v2.2", V2_3:"v2.3", V2_4:"v2.4", V2:"v2.x"}

LATIN1_ENCODING   = b"\x00"
UTF_16_ENCODING   = b"\x01"
UTF_16BE_ENCODING = b"\x02"
UTF_8_ENCODING    = b"\x03"

DEFAULT_LANG = b"eng"

GENRES = ['Blues',
          'Classic Rock',
          'Country',
          'Dance',
          'Disco',
          'Funk',
          'Grunge',
          'Hip-Hop',
          'Jazz',
          'Metal',
          'New Age',
          'Oldies',
          'Other',
          'Pop',
          'R&B',
          'Rap',
          'Reggae',
          'Rock',
          'Techno',
          'Industrial',
          'Alternative',
          'Ska',
          'Death Metal',
          'Pranks',
          'Soundtrack',
          'Euro-Techno',
          'Ambient',
          'Trip-Hop',
          'Vocal',
          'Jazz+Funk',
          'Fusion',
          'Trance',
          'Classical',
          'Instrumental',
          'Acid',
          'House',
          'Game',
          'Sound Clip',
          'Gospel',
          'Noise',
          'AlternRock',
          'Bass',
          'Soul',
          'Punk',
          'Space',
          'Meditative',
          'Instrumental Pop',
          'Instrumental Rock',
          'Ethnic',
          'Gothic',
          'Darkwave',
          'Techno-Industrial',
          'Electronic',
          'Pop-Folk',
          'Eurodance',
          'Dream',
          'Southern Rock',
          'Comedy',
          'Cult',
          'Gangsta Rap',
          'Top 40',
          'Christian Rap',
          'Pop / Funk',
          'Jungle',
          'Native American',
          'Cabaret',
          'New Wave',
          'Psychedelic',
          'Rave',
          'Showtunes',
          'Trailer',
          'Lo-Fi',
          'Tribal',
          'Acid Punk',
          'Acid Jazz',
          'Polka',
          'Retro',
          'Musical',
          'Rock & Roll',
          'Hard Rock',
          'Folk',
          'Folk-Rock',
          'National Folk',
          'Swing',
          'Fast  Fusion',
          'Bebob',
          'Latin',
          'Revival',
          'Celtic',
          'Bluegrass',
          'Avantgarde',
          'Gothic Rock',
          'Progressive Rock',
          'Psychedelic Rock',
          'Symphonic Rock',
          'Slow Rock',
          'Big Band',
          'Chorus',
          'Easy Listening',
          'Acoustic',
          'Humour',
          'Speech',
          'Chanson',
          'Opera',
          'Chamber Music',
          'Sonata',
          'Symphony',
          'Booty Bass',
          'Primus',
          'Porn Groove',
          'Satire',
          'Slow Jam',
          'Club',
          'Tango',
          'Samba',
          'Folklore',
          'Ballad',
          'Power Ballad',
          'Rhythmic Soul',
          'Freestyle',
          'Duet',
          'Punk Rock',
          'Drum Solo',
          'A Cappella',
          'Euro-House',
          'Dance Hall',
          'Goa',
          'Drum & Bass',
          'Club-House',
          'Hardcore',
          'Terror',
          'Indie',
          'BritPop',
          'Negerpunk',
          'Polsk Punk',
          'Beat',
          'Christian Gangsta Rap',
          'Heavy Metal',
          'Black Metal',
          'Crossover',
          'Contemporary Christian',
          'Christian Rock',
          'Merengue',
          'Salsa',
          'Thrash Metal',
          'Anime',
          'JPop',
          'Synthpop',
          'Rock/Pop']

#--------------------------------------------------------------------------------------------------#

def isValidVersion(v, fully_qualified=False):
    valid = v in [V1, V1_0, V1_1, V2, V2_2, V2_3, V2_4, ANY_VERSION]
    
    if not valid:
        return False

    if fully_qualified:
        return (None not in (v[0], v[1], v[2]))    
    else:
        return True

#--------------------------------------------------------------------------------------------------#

def normalizeVersion(version):
    if version == V1:
        version = V1_1
    elif version == V2:
        assert(DEFAULT_VERSION[0] & V2[0])
        version = DEFAULT_VERSION
    elif version == ANY_VERSION:
        version = DEFAULT_VERSION

    if version[:2] == (2, 2) and version[2] != 0:
        version = (2, 2, 0)

    return version


def versionToString(version):
    if version == ANY_VERSION:
        return "v1.x/v2.x"

    try:
        return VERSION_LOOKUP[version]
    except KeyError:
        raise ValueError("Invalid ID3 version constant: %s." %version)

#--------------------------------------------------------------------------------------------------#
    
class GenreError(Exception):
    pass

#--------------------------------------------------------------------------------------------------#

class Genre():
    def __init__(self, name=None, id=None):
        self.id, self.name = None, None
        if not name and id is None:
            return
        
        if id is not None:
            try:
                self.id = id
                assert(self.name)
            except ValueError as e:
                if not name: raise e
                self.name = name
                self.id = None
        else:
            self.name = name

        assert(self.id or self.name)
        
        
    @property
    def id(self):
        return self._id
    
    
    @id.setter
    def id(self, id):
        global genres

        if id is None:
            self._id = None
            return

        id = int(id)
        if id not in list(genres.keys()):
            raise ValueError("Invalid numeric genre ID: %d" %id)

        name = genres[id]
        self._id   = id
        self._name = name
    
    
    @property
    def name(self):
        return self._name    
    
    
    @name.setter
    def name(self, name):
        global genres
        if name is None:
            self._name = None
            return

        if name.lower() in list(genres.keys()):
            self._id = genres[name]
            self._name = genres[self._id]
        else:
            self._id = None
            self._name = name
            
            
    @staticmethod
    def parse(genre_str):
        genre_str = genre_str.strip()
        if not genre_str:
            return None

        def stripPadding(s):
            if len(s) > 1:
                return s.lstrip("0")
            else:
                return s

        regex = re.compile("[0-9][0-9]*$")
        if regex.match(genre_str):
            return Genre(id=int(stripPadding(genre_str)))

        regex = re.compile("\(([0-9][0-9]*)\)(.*)$")
        match = regex.match(genre_str)
        if match:
            id, name = match.groups()

            id = int(stripPadding(id))
            if id and name:
                id = id
                name = name.strip()
            else:
                id = id
                name = None

            return Genre(id=id, name=name)

        return Genre(id=None, name=genre_str)
    
    
    def __unicode__(self):
        s = ""
        if self.id != None:
            s += "(%d)" %self.id
        if self.name:
            s += self.name
        return s


    def __eq__(self, rhs):
        return self.id == rhs.id and self.name == rhs.name


    def __ne__(self, rhs):
        return not self.__eq__(rhs)

#--------------------------------------------------------------------------------------------------#

class GenreMap(dict):
    GENRE_MIN        = 0
    GENRE_MAX        = None
    ID3_GENRE_MIN    = 0
    ID3_GENRE_MAX    = 79
    WINAMP_GENRE_MIN = 80
    WINAMP_GENRE_MAX = 147

    def __init__(self, *args):
        global GENRES
        super(GenreMap, self).__init__(*args)

        for i, g in enumerate(GENRES):
            self[i] = g
            self[g.lower()] = i

        GenreMap.GENRE_MAX = len(GENRES) - 1
        for i in range(GenreMap.GENRE_MAX + 1, 255 + 1):
            self[i] = "<not-set>"
        self["<not-set>".lower()] = 255


    def __getitem__(self, key):
        if type(key) is not int:
            key = key.lower()
        return super(GenreMap, self).__getitem__(key)
    
genres = GenreMap()
    
#--------------------------------------------------------------------------------------------------#

class TagFile(core.AudioFile):
    def __init__(self, path, version=ANY_VERSION):
        self._tag_version = version
        core.AudioFile.__init__(self, path)
        assert(self.type == core.AUDIO_NONE)


    def _read(self):
        from .tag import Tag

        with file(self.path, 'rb') as file_obj:
            tag = Tag()
            tag_found = tag.parse(file_obj, self._tag_version)
            self._tag = tag if tag_found else None

        self.type = core.AUDIO_NONE


    def initTag(self, version=DEFAULT_VERSION):
        from .tag import Tag, FileInfo
        self.tag = Tag()
        self.tag.version = version
        self.tag.file_info = FileInfo(self.path)
    