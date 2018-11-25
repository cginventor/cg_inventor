import os, types, string, shutil, tempfile

from cg_inventor.sys.utils.audio         import Error, core
from cg_inventor.sys.utils.audio.utils   import chunkCopy, datePickerError
from cg_inventor.sys.utils.audio.core    import TXXX_ALBUM_TYPE, TXXX_ARTIST_ORIGIN, ALBUM_TYPE_IDS
from cg_inventor.sys.utils.audio.id3     import (ID3_ANY_VERSION, ID3_V1, ID3_V1_0, ID3_V1_1,
                                                ID3_V2, ID3_V2_2, ID3_V2_3, ID3_V2_4, 
                                                versionToString, DEFAULT_LANG, Genre, frames)
from cg_inventor.sys.utils.audio.headers import TagHeader, ExtendedTagHeader
#from cg_inventor.sys.utils.audio.compat  import StringTypes, BytesType, unicode, UnicodeType

#--------------------------------------------------------------------------------------------------#

class TagException(Exception):
    pass

#--------------------------------------------------------------------------------------------------#

class Tag(core.Tag):
    def __init__(self):
        core.Tag.__init__(self)
        self.clear()

    #------------------------------------------------------------------------------------------#    

    def clear(self):
        self.header = TagHeader()
        self.extended_header = ExtendedTagHeader()
        
        self.frame_set        = frames.FrameSet()
        self._comments        = CommentsAccessor(self.frame_set)
        self._images          = ImagesAccessor(self.frame_set)
        self._lyrics          = LyricsAccessor(self.frame_set)
        self._objects         = ObjectsAccessor(self.frame_set)
        self._privates        = PrivatesAccessor(self.frame_set)
        self._user_texts      = UserTextsAccessor(self.frame_set)
        self._unique_file_ids = UniqueFileIdAccessor(self.frame_set)
        self._user_urls       = UserUrlsAccessor(self.frame_set)
        self._chapters        = ChaptersAccessor(self.frame_set)
        self._tocs            = TocAccessor(self.frame_set)
        self._popularities    = PopularitiesAccessor(self.frame_set)
        self.file_info        = None

    #------------------------------------------------------------------------------------------#   
    
    def parse(self, fileobj, version=ID3_ANY_VERSION):
        assert(fileobj)
        self.clear()
        version = version or ID3_ANY_VERSION

        close_file = False
        try:
            filename = fileobj.name
        except AttributeError:
            if type(fileobj) is str:
                filename = fileobj
                fileobj = open(filename, "rb")
                close_file = True
            else:
                raise ValueError("Invalid type: %s" % str(type(fileobj)))

        self.file_info = FileInfo(filename)

        try:
            tag_found = False
            padding = 0

            if version[0] & 2:
                tag_found, padding = self._loadV2Tag(fileobj)

            if not tag_found and version[0] & 1:
                tag_found, padding = self._loadV1Tag(fileobj)
                if tag_found:
                    self.extended_header = None

            if tag_found and self.isV2():
                self.file_info.tag_size = (TagHeader.SIZE +
                                           self.header.tag_size)
            if tag_found:
                self.file_info.tag_padding_size = padding

        finally:
            if close_file:
                fileobj.close()

        return tag_found

    #------------------------------------------------------------------------------------------#   
    
    def _loadV2Tag(self, fp):
        padding = 0
        if not self.header.parse(fp):
            return (False, 0)

        if self.header.extended:
            self.extended_header.parse(fp, self.header.version)

        padding = self.frame_set.parse(fp, self.header,
                                       self.extended_header)

        return (True, padding)

    #------------------------------------------------------------------------------------------#   
    
    def _loadV1Tag(self, fp):
        v1_enc = "latin1"

        fp.seek(0, 2)
        if fp.tell() < 128:
            return (False, 0)
        fp.seek(-128, 2)
        tag_data = fp.read(128)

        if tag_data[0:3] != "TAG":
            return (False, 0)

        self.version = ID3_V1_0

        STRIP_CHARS = string.whitespace + "\x00"
        title = tag_data[3:33].strip(STRIP_CHARS)
        if title:
            self.title = str(title, v1_enc)

        artist = tag_data[33:63].strip(STRIP_CHARS)
        if artist:
            self.artist = str(artist, v1_enc)

        album = tag_data[63:93].strip(STRIP_CHARS)
        if album:
            self.album = str(album, v1_enc)

        year = tag_data[93:97].strip(STRIP_CHARS)
        try:
            if year and int(year):
                self.release_date = int(year)
        except ValueError:
            pass

        comment = tag_data[97:127].rstrip("\x00")
        if comment:
            if (len(comment) >= 2 and
                    comment[-2] == "\x00" and comment[-1] != "\x00"):
                log.debug("Track Num found, setting version to v1.1")
                self.version = ID3_V1_1

                track = ord(comment[-1])
                self.track_num = (track, None)
                log.debug("Track: " + str(track))
                comment = comment[:-2].strip(STRIP_CHARS)

            if comment:
                log.debug("Comment: %s" % comment)
                self.comments.set(str(comment, v1_enc), ID3_V1_COMMENT_DESC)

        genre = ord(tag_data[127:128])
        log.debug("Genre ID: %d" % genre)
        try:
            self.genre = genre
        except ValueError as ex:
            log.warning(ex)
            self.genre = None

        return (True, 0)
    
    #------------------------------------------------------------------------------------------#  

    @property
    def version(self):
        return self.header.version

    @version.setter
    def version(self, v):
        self.header.version = v


    def isV1(self):
        return self.header.major_version == 1


    def isV2(self):
        return self.header.major_version == 2    

    #------------------------------------------------------------------------------------------#  
    
    def setTextFrame(self, fid, txt):
        if not fid.startswith("T") or fid.startswith("TX"):
            raise ValueError("Invalid frame-id for text frame: " +
                             str(fid, "ascii"))

        if not txt and self.frame_set[fid]:
            del self.frame_set[fid]
        elif txt:
            self.frame_set.setTextFrame(fid, txt)


    def getTextFrame(self, fid):
        if not fid.startswith("T") or fid.startswith("TX"):
            raise ValueError("Invalid frame-id for text frame: " +
                             str(fid, "ascii"))
        f = self.frame_set[fid]
        return f[0].text if f else None

    #------------------------------------------------------------------------------------------#  
        
    def _setArtist(self, val):
        self.setTextFrame(frames.ARTIST_FID, val)


    def _getArtist(self):
        return self.getTextFrame(frames.ARTIST_FID)


    def _setAlbumArtist(self, val):
        self.setTextFrame(frames.ALBUM_ARTIST_FID, val)


    def _getAlbumArtist(self):
        return self.getTextFrame(frames.ALBUM_ARTIST_FID)


    def _setAlbum(self, val):
        self.setTextFrame(frames.ALBUM_FID, val)


    def _getAlbum(self):
        return self.getTextFrame(frames.ALBUM_FID)


    def _setTitle(self, val):
        self.setTextFrame(frames.TITLE_FID, val)


    def _getTitle(self):
        return self.getTextFrame(frames.TITLE_FID)


    def _setTrackNum(self, val):
        self._setNum(frames.TRACKNUM_FID, val)


    def _getTrackNum(self):
        return self._splitNum(frames.TRACKNUM_FID)    
    
    
    def _splitNum(self, fid):
        f = self.frame_set[fid]
        first, second = None, None
        if f and f[0].text:
            n = f[0].text.split('/')
            try:
                first = int(n[0])
                second = int(n[1]) if len(n) == 2 else None
            except ValueError as ex:
                log.warning(str(ex))
        return (first, second)
    
    
    def _setNum(self, fid, val):
        if type(val) is tuple:
            tn, tt = val
        elif type(val) is int:
            tn, tt = val, None
        elif val is None:
            tn, tt = None, None

        n = (tn, tt)

        if n[0] is None and n[1] is None:
            if self.frame_set[fid]:
                del self.frame_set[fid]
            return

        total_str = ""
        if n[1] is not None:
            if n[1] >= 0 and n[1] <= 9:
                total_str = "0" + str(n[1])
            else:
                total_str = str(n[1])

        t = n[0] if n[0] else 0
        track_str = str(t)

        if len(track_str) == 1:
            track_str = "0" + track_str
        if len(track_str) < len(total_str):
            track_str = ("0" * (len(total_str) - len(track_str))) + track_str

        final_str = ""
        if track_str and total_str:
            final_str = "%s/%s" % (track_str, total_str)
        elif track_str and not total_str:
            final_str = track_str

        self.frame_set.setTextFrame(fid, str(final_str))

    #------------------------------------------------------------------------------------------#  
        
    @property
    def comments(self):
        return self._comments

    #------------------------------------------------------------------------------------------#  

    @property
    def bpm(self):
        bpm = None
        if frames.BPM_FID in self.frame_set:
            bpm_str = self.frame_set[frames.BPM_FID][0].text or u"0"
            try:
                bpm = int(round(float(bpm_str)))
            except ValueError as ex:
                log.warning(ex)
        return bpm
    
    
    @play_count.bpm
    def bpm(self, bpm):
        assert(bpm >= 0)
        self.setTextFrame(frames.BPM_FID, str(str(bpm)))

    #------------------------------------------------------------------------------------------#  
    
    @property
    def play_count(self):
        if frames.PLAYCOUNT_FID in self.frame_set:
            pc = self.frame_set[frames.PLAYCOUNT_FID][0]
            return pc.count
        else:
            return None
        
        
    @play_count.setter
    def play_count(self, count):
        if count is None:
            del self.frame_set[frames.PLAYCOUNT_FID]
            return

        if count < 0:
            raise ValueError("Invalid play count value: %d" % count)

        if self.frame_set[frames.PLAYCOUNT_FID]:
            pc = self.frame_set[frames.PLAYCOUNT_FID][0]
            pc.count = count
        else:
            self.frame_set[frames.PLAYCOUNT_FID] = \
                frames.PlayCountFrame(count=count)
    
    #------------------------------------------------------------------------------------------#  
    
    @property
    def publisher(self):
        if frames.PUBLISHER_FID in self.frame_set:
            pub = self.frame_set[frames.PUBLISHER_FID]
            return pub[0].text
        else:
            return None


    @play_count.publisher
    def publisher(self, p):
        self.setTextFrame(frames.PUBLISHER_FID, p)

    #------------------------------------------------------------------------------------------#  

    @property
    def cd_id(self):
        if frames.CDID_FID in self.frame_set:
            return self.frame_set[frames.CDID_FID][0].toc
        else:
            return None


    @cd_id.setter
    def cd_id(self, toc):
        if len(toc) > 804:
            raise ValueError("CD identifier table of contents can be no "
                             "greater than 804 bytes")

        if self.frame_set[frames.CDID_FID]:
            cdid = self.frame_set[frames.CDID_FID][0]
            cdid.toc = str(toc)
        else:
            self.frame_set[frames.CDID_FID] = \
                frames.MusicCDIdFrame(toc=toc)
                
    #------------------------------------------------------------------------------------------#  

    @property
    def images(self):
        return self._images


    @property
    def encoding_date(self):
        return self._getDate("TDEN")


    @encoding_date.setter
    def encoding_date(self, date):
        self._setDate("TDEN", date)

    #------------------------------------------------------------------------------------------#  

    @property
    def best_release_date(self):
        return (self.original_release_date or
                self.release_date or
                self.recording_date)


    def getBestDate(self, prefer_recording_date=False):
        return datePicker(self, prefer_recording_date)


    @property
    def release_date(self):
        return self._getDate("TDRL") if self.version == ID3_V2_4 \
                                     else self._getV23OrignalReleaseDate()


    @release_date.setter
    def release_date(self, date):
        self._setDate("TDRL" if self.version == ID3_V2_4 else "TORY", date)


    @property
    def original_release_date(self):
        return self._getDate("TDOR") or self._getV23OrignalReleaseDate()


    @original_release_date.setter
    def original_release_date(self, date):
        self._setDate("TDOR", date)


    @property
    def recording_date(self):
        return self._getDate("TDRC") or self._getV23RecordingDate()


    @property.setter
    def recording_date(self, date):
        if date is None:
            for fid in ("TDRC", "TYER", "TDAT", "TIME"):
                self._setDate(fid, None)
                
        elif self.version == ID3_V2_4:
            self._setDate("TDRC", date)
            
        else:
            self._setDate("TYER", str(date.year))
            if None not in (date.month, date.day):
                date_str = u"%s%s" % (str(date.day).rjust(2, "0"),
                                      str(date.month).rjust(2, "0"))
                self._setDate("TDAT", date_str)
            if None not in (date.hour, date.minute):
                date_str = u"%s%s" % (str(date.hour).rjust(2, "0"),
                                      str(date.minute).rjust(2, "0"))
                self._setDate("TIME", date_str)
                
                
    def _getV23RecordingDate(self):
        date = None
        try:
            date_str = ""
            if "TYER" in self.frame_set:
                date_str = self.frame_set["TYER"][0].text.encode("latin1")
                date = core.Date.parse(date_str)
            if "TDAT" in self.frame_set:
                text = self.frame_set["TDAT"][0].text.encode("latin1")
                date_str += "-%s-%s" % (text[2:], text[:2])
                date = core.Date.parse(date_str)
            if "TIME" in self.frame_set:
                text = self.frame_set["TIME"][0].text.encode("latin1")
                date_str += "T%s:%s" % (text[:2], text[2:])
                date = core.Date.parse(date_str)
        except ValueError as ex:
            log.warning("Invalid v2.3 TYER, TDAT, or TIME frame: %s" % ex)

        return date


    def _getV23OrignalReleaseDate(self):
        date, date_str = None, None
        try:
            for fid in ("XDOR", "TORY"):
                if fid in self.frame_set:
                    date_str = self.frame_set[fid][0].text.encode("latin1")
                    break
            if date_str:
                date = core.Date.parse(date_str)
        except ValueError as ex:
            log.warning("Invalid v2.3 TORY/XDOR frame: %s" % ex)

        return date
    
    #------------------------------------------------------------------------------------------#
    
    def _getTaggingDate(self):
        return self._getDate("TDTG")


    def _setTaggingDate(self, date):
        self._setDate("TDTG", date)
    tagging_date = property(_getTaggingDate, _setTaggingDate)
    
    #------------------------------------------------------------------------------------------#

    def _setDate(self, fid, date):
        assert(fid in frames.DATE_FIDS or
               fid in frames.DEPRECATED_DATE_FIDS)

        if date is None:
            try:
                del self.frame_set[fid]
            except KeyError:
                pass
            return

        if fid not in ("TDAT", "TIME"):
            date_type = type(date)
            if date_type is int:
                date = core.Date(date)
            elif date_type is str:
                date = core.Date.parse(date)
            elif not isinstance(date, core.Date):
                raise TypeError("Invalid type: %s" % str(type(date)))

        date_text = str(str(date))
        if fid in self.frame_set:
            self.frame_set[fid][0].date = date
        else:
            self.frame_set[fid] = frames.DateFrame(fid, date_text)


    def _getDate(self, fid):
        if fid in ("TORY", "XDOR"):
            return self._getV23OrignalReleaseDate()

        if fid in self.frame_set:
            if fid in ("TYER", "TDAT", "TIME"):
                if fid == "TYER":
                    # Contain years only, date conversion can happen
                    return core.Date(int(self.frame_set[fid][0].text))
                else:
                    return self.frame_set[fid][0].text
            else:
                return self.frame_set[fid][0].date
        else:
            return None
        
    #------------------------------------------------------------------------------------------#

    @property
    def lyrics(self):
        return self._lyrics

    @property
    def disc_num(self):
        return self._splitNum(frames.DISCNUM_FID)

    @disc_num.setter
    def disc_num(self, val):
        self._setNum(frames.DISCNUM_FID, val)
        
    @property
    def objects(self):
        return self._objects

    @property
    def privates(self):
        return self._privates

    @property
    def popularities(self):
        return self._popularities
    
    #------------------------------------------------------------------------------------------#

    def _getGenre(self):
        f = self.frame_set[frames.GENRE_FID]
        if f and f[0].text:
            return Genre.parse(f[0].text)
        else:
            return None

    def _setGenre(self, g):
        if g is None:
            if self.frame_set[frames.GENRE_FID]:
                del self.frame_set[frames.GENRE_FID]
            return

        if isinstance(g, str):
            g = Genre.parse(g)
        elif isinstance(g, int):
            g = Genre(id=g)
        elif not isinstance(g, Genre):
            raise TypeError("Invalid genre data type: %s" % str(type(g)))
        self.frame_set.setTextFrame(frames.GENRE_FID, str(g))
    genre = property(_getGenre, _setGenre)

    #------------------------------------------------------------------------------------------#
    
    @property
    def user_text_frames(self):
        return self._user_texts

    def _setUrlFrame(self, fid, url):
        if fid not in frames.URL_FIDS:
            raise ValueError("Invalid URL frame-id")

        if self.frame_set[fid]:
            if not url:
                del self.frame_set[fid]
            else:
                self.frame_set[fid][0].url = url
        else:
            self.frame_set[fid] = frames.UrlFrame(fid, url)

    def _getUrlFrame(self, fid):
        if fid not in frames.URL_FIDS:
            raise ValueError("Invalid URL frame-id")
        f = self.frame_set[fid]
        return f[0].url if f else None
    
    #------------------------------------------------------------------------------------------#

    @property
    def commercial_url(self):
        return self._getUrlFrame(frames.URL_COMMERCIAL_FID)

    @commercial_url.setter
    def commercial_url(self, url):
        self._setUrlFrame(frames.URL_COMMERCIAL_FID, url)

    @property
    def copyright_url(self):
        return self._getUrlFrame(frames.URL_COPYRIGHT_FID)

    @copyright_url.setter
    def copyright_url(self, url):
        self._setUrlFrame(frames.URL_COPYRIGHT_FID, url)

    @property
    def audio_file_url(self):
        return self._getUrlFrame(frames.URL_AUDIOFILE_FID)

    @audio_file_url.setter
    def audio_file_url(self, url):
        self._setUrlFrame(frames.URL_AUDIOFILE_FID, url)

    @property
    def audio_source_url(self):
        return self._getUrlFrame(frames.URL_AUDIOSRC_FID)

    @audio_source_url.setter
    def audio_source_url(self, url):
        self._setUrlFrame(frames.URL_AUDIOSRC_FID, url)

    @property
    def artist_url(self):
        return self._getUrlFrame(frames.URL_ARTIST_FID)

    @artist_url.setter
    def artist_url(self, url):
        self._setUrlFrame(frames.URL_ARTIST_FID, url)

    @property
    def internet_radio_url(self):
        return self._getUrlFrame(frames.URL_INET_RADIO_FID)

    @internet_radio_url.setter
    def internet_radio_url(self, url):
        self._setUrlFrame(frames.URL_INET_RADIO_FID, url)

    @property
    def payment_url(self):
        return self._getUrlFrame(frames.URL_PAYMENT_FID)

    @payment_url.setter
    def payment_url(self, url):
        self._setUrlFrame(frames.URL_PAYMENT_FID, url)

    @property
    def publisher_url(self):
        return self._getUrlFrame(frames.URL_PUBLISHER_FID)

    @publisher_url.setter
    def publisher_url(self, url):
        self._setUrlFrame(frames.URL_PUBLISHER_FID, url)

    @property
    def user_url_frames(self):
        return self._user_urls
    
    @property
    def unique_file_ids(self):
        return self._unique_file_ids

    @property
    def terms_of_use(self):
        if self.frame_set[frames.TOS_FID]:
            return self.frame_set[frames.TOS_FID][0].text

    @terms_of_use.setter
    @reqstrcode(1)
    def terms_of_use(self, tos):
        if self.frame_set[frames.TOS_FID]:
            self.frame_set[frames.TOS_FID][0].text = tos
        else:
            self.frame_set[frames.TOS_FID] = frames.TermsOfUseFrame(text=tos)
            
    def _raiseIfReadonly(self):
        if self.read_only:
            raise RuntimeError("Tag is set read only.")
    
    #------------------------------------------------------------------------------------------#
    
    def save(self, filename           = None, 
                   version            = None, 
                   encoding           = None, 
                   backup             = False,
                   preserve_file_time = False, 
                   max_padding        = None):
        self._raiseIfReadonly()

        if not (filename or self.file_info):
            raise TagException("No file")
        elif filename:
            self.file_info = FileInfo(filename)

        version = version if version else self.version
        if version == ID3_V2_2:
            raise NotImplementedError("Unable to write ID3 v2.2")
        self.version = version

        if backup and os.path.isfile(self.file_info.name):
            backup_name = "%s.%s" % (self.file_info.name, "orig")
            i = 1
            while os.path.isfile(backup_name):
                backup_name = "%s.%s.%d" % (self.file_info.name, "orig", i)
                i += 1
            shutil.copyfile(self.file_info.name, backup_name)

        if version[0] == 1:
            self._saveV1Tag(version)
        elif version[0] == 2:
            self._saveV2Tag(version, encoding, max_padding)
        else:
            assert(not "Version bug: %s" % str(version))

        if preserve_file_time and None not in (self.file_info.atime,
                                               self.file_info.mtime):
            self.file_info.touch((self.file_info.atime, self.file_info.mtime))
        else:
            self.file_info.initStatTimes()
            
            
    def _saveV1Tag(self, version):
        self._raiseIfReadonly()

        assert(version[0] == 1)

        def pack(s, n):
            assert(type(s) is str)
            return s.ljust(n, '\x00')[:n]

        tag = b"TAG"
        tag += pack(self.title.encode("latin_1") if self.title else b"", 30)
        tag += pack(self.artist.encode("latin_1") if self.artist else b"", 30)
        tag += pack(self.album.encode("latin_1") if self.album else b"", 30)

        release_date = self.getBestDate()
        year = str(release_date.year) if release_date else b""
        tag += pack(year.encode("latin_1"), 4)

        cmt = ""
        for c in self.comments:
            if c.description == ID3_V1_COMMENT_DESC:
                cmt = c.text
                break
            elif c.description == "":
                cmt = c.text
        cmt = pack(cmt.encode("latin_1"), 30)

        if version != ID3_V1_0:
            track = self.track_num[0]
            if track is not None:
                cmt = cmt[0:28] + "\x00" + chr(int(track) & 0xff)
        tag += cmt

        if not self.genre or self.genre.id is None:
            genre = 12  # Other
        else:
            genre = self.genre.id
        tag += chr(genre & 0xff)

        assert(len(tag) == 128)

        mode = "rb+" if os.path.isfile(self.file_info.name) else "w+b"
        with open(self.file_info.name, mode) as tag_file:
            try:
                tag_file.seek(-128, 2)
                if tag_file.read(3) == "TAG":
                    tag_file.seek(-128, 2)
                else:
                    tag_file.seek(0, 2)
            except IOError:
                tag_file.seek(0, 2)

            tag_file.write(tag)
            tag_file.flush()

    def _render(self, version, curr_tag_size, max_padding_size):
        std_frames = []
        non_std_frames = []
        for f in self.frame_set.getAllFrames():
            try:
                _, fversion, _ = frames.ID3_FRAMES[f.id]
                if fversion in (version, ID3_V2):
                    std_frames.append(f)
                else:
                    non_std_frames.append(f)
            except KeyError:
                try:
                    _, fversion, _ = frames.NONSTANDARD_ID3_FRAMES[f.id]
                    if fversion in (version, ID3_V2):
                        std_frames.append(f)
                    else:
                        non_std_frames.append(f)
                except KeyError:
                    non_std_frames.append(f)

        if non_std_frames:
            non_std_frames = self._convertFrames(std_frames, non_std_frames,
                                                 version)

        frame_data = b""
        for f in std_frames + non_std_frames:
            frame_header = frames.FrameHeader(f.id, version)
            if f.header:
                frame_header.copyFlags(f.header)
            f.header = frame_header

            log.debug("Rendering frame: %s" % frame_header.id)
            raw_frame = f.render()
            log.debug("Rendered %d bytes" % len(raw_frame))
            frame_data += raw_frame

        log.debug("Rendered %d total frame bytes" % len(frame_data))

        self.header.unsync = False

        pending_size = TagHeader.SIZE + len(frame_data)
        if self.header.extended:
            tmp_ext_header_data = self.extended_header.render(version,
                                                              b"\x00", 0)
            pending_size += len(tmp_ext_header_data)

        padding_size = 0
        if pending_size > curr_tag_size:
            padding_size = DEFAULT_PADDING
            rewrite_required = True
        else:
            padding_size = curr_tag_size - pending_size
            if max_padding_size is not None and padding_size > max_padding_size:
                padding_size = min(DEFAULT_PADDING, max_padding_size)
                rewrite_required = True
            else:
                rewrite_required = False

        assert(padding_size >= 0)
        log.debug("Using %d bytes of padding" % padding_size)

        ext_header_data = b""
        if self.header.extended:
            log.debug("Rendering extended header")
            ext_header_data += self.extended_header.render(self.header.version,
                                                           frame_data,
                                                           padding_size)

        total_size = pending_size + padding_size
        log.debug("Rendering %s tag header with size %d" %
                  (versionToString(version),
                   total_size - TagHeader.SIZE))
        header_data = self.header.render(total_size - TagHeader.SIZE)

        # Assemble the entire tag.
        tag_data = b"%(tag_header)s%(ext_header)s%(frames)s" % \
                   {"tag_header": header_data,
                    "ext_header": ext_header_data,
                    "frames": frame_data,
                    }
        assert(len(tag_data) == (total_size - padding_size))
        return (rewrite_required, tag_data, "\x00" * padding_size)
    
    
    def _saveV2Tag(self, version, encoding, max_padding):
        self._raiseIfReadonly()

        assert(version[0] == 2 and version[1] != 2)

        log.debug("Rendering tag version: %s" % versionToString(version))

        file_exists = os.path.exists(self.file_info.name)

        if encoding:
            for f in self.frame_set.getAllFrames():
                f.encoding = frames.stringToEncoding(encoding)

        curr_tag_size = 0

        if file_exists:
            tmp_tag = Tag()
            if tmp_tag.parse(self.file_info.name, ID3_V2):
                log.debug("Found current v2.x tag:")
                curr_tag_size = tmp_tag.file_info.tag_size
                log.debug("Current tag size: %d" % curr_tag_size)

            rewrite_required, tag_data, padding = self._render(version,
                                                               curr_tag_size,
                                                               max_padding)
            if rewrite_required:
                with tempfile.NamedTemporaryFile("wb", delete=False) \
                        as tmp_file:
                    tmp_file.write(tag_data + padding)

                    with open(self.file_info.name, "rb") as tag_file:
                        if curr_tag_size != 0:
                            seek_point = curr_tag_size
                        else:
                            seek_point = 0
                        tag_file.seek(seek_point)
                        chunkCopy(tag_file, tmp_file)

                    tmp_file.flush()

                shutil.copyfile(tmp_file.name, self.file_info.name)
                os.unlink(tmp_file.name)

            else:
                with open(self.file_info.name, "r+b") as tag_file:
                    tag_file.write(tag_data + padding)

        else:
            _, tag_data, padding = self._render(version, 0, None)
            with open(self.file_info.name, "wb") as tag_file:
                tag_file.write(tag_data + padding)

        self.file_info.tag_size = len(tag_data) + len(padding)

    #------------------------------------------------------------------------------------------#
        
    def _convertFrames(self, std_frames, convert_list, version):
        from . import versionToString
        from .frames import (DATE_FIDS, DEPRECATED_DATE_FIDS,
                             DateFrame, TextFrame)
        converted_frames = []
        flist = list(convert_list)

        date_frames = {}
        for f in flist:
            if version == ID3_V2_4:
                if f.id in DEPRECATED_DATE_FIDS:
                    date_frames[f.id] = f
            else:
                if f.id in DATE_FIDS:
                    date_frames[f.id] = f

        if date_frames:
            if version == ID3_V2_4:
                if "TORY" in date_frames or "XDOR" in date_frames:
                    date = self._getV23OrignalReleaseDate()
                    if date:
                        converted_frames.append(DateFrame("TDOR", date))
                    for fid in ("TORY", "XDOR"):
                        if fid in flist:
                            flist.remove(date_frames[fid])
                            del date_frames[fid]

                if ("TYER" in date_frames or "TDAT" in date_frames or
                        "TIME" in date_frames):
                    date = self._getV23RecordingDate()
                    if date:
                        converted_frames.append(DateFrame("TDRC", date))
                    for fid in ["TYER", "TDAT", "TIME"]:
                        if fid in date_frames:
                            flist.remove(date_frames[fid])
                            del date_frames[fid]

            elif version == ID3_V2_3:
                if "TDOR" in date_frames:
                    date = date_frames["TDOR"].date
                    if date:
                        converted_frames.append(DateFrame("TORY",
                                                          str(date.year)))
                    flist.remove(date_frames["TDOR"])
                    del date_frames["TDOR"]

                if "TDRC" in date_frames:
                    date = date_frames["TDRC"].date

                    if date:
                        converted_frames.append(DateFrame("TYER",
                                                          str(date.year)))
                        if None not in (date.month, date.day):
                            date_str = u"%s%s" %\
                                    (str(date.day).rjust(2, "0"),
                                     str(date.month).rjust(2, "0"))
                            converted_frames.append(TextFrame("TDAT", date_str))
                        if None not in (date.hour, date.minute):
                            date_str = u"%s%s" %\
                                    (str(date.hour).rjust(2, "0"),
                                     str(date.minute).rjust(2, "0"))
                            converted_frames.append(TextFrame("TIME", date_str))

                    flist.remove(date_frames["TDRC"])
                    del date_frames["TDRC"]

                if "TDRL" in date_frames:
                    # TDRL -> XDOR
                    date = date_frames["TDRL"].date
                    if date:
                        converted_frames.append(DateFrame("XDOR", str(date)))
                    flist.remove(date_frames["TDRL"])
                    del date_frames["TDRL"]

            for fid in date_frames:
                log.warning("%s frame being dropped due to conversion to %s" %
                            (fid, versionToString(version)))
                flist.remove(date_frames[fid])

        prefix = "X" if version == ID3_V2_4 else "T"
        fids = ["%s%s" % (prefix, suffix) for suffix in ["SOA", "SOP", "SOT"]]
        soframes = [f for f in flist if f.id in fids]

        for frame in soframes:
            frame.id = ("X" if prefix == "T" else "T") + frame.id[1:]
            flist.remove(frame)
            converted_frames.append(frame)

        if version == ID3_V2_4:
            flist = [f for f in flist if f.id != "TSIZ"]

        if version == ID3_V2_3 and "TSST" in [f.id for f in flist]:
            tsst_frame = [f for f in flist if f.id == "TSST"][0]
            flist.remove(tsst_frame)
            tsst_frame = frames.UserTextFrame(
                    description=u"Subtitle (converted)", text=tsst_frame.text)
            converted_frames.append(tsst_frame)

        if len(flist) != 0:
            unconverted = ", ".join([f.id for f in flist])
            raise TagException("Unable to covert the following frames to "
                               "version %s: %s" % (versionToString(version),
                                                   unconverted))

        for cframe in converted_frames:
            for sframe in std_frames:
                if cframe.id == sframe.id:
                    std_frames.remove(sframe)

        return converted_frames

    #------------------------------------------------------------------------------------------#
    
    @staticmethod
    def remove(filename, version=ID3_ANY_VERSION, preserve_file_time=False):
        retval = False

        if version[0] & ID3_V1[0]:
            # ID3 v1.x
            tag = Tag()
            with open(filename, "r+b") as tag_file:
                found = tag.parse(tag_file, ID3_V1)
                if found:
                    tag_file.seek(-128, 2)
                    log.debug("Removing ID3 v1.x Tag")
                    tag_file.truncate()
                    retval |= True

        if version[0] & ID3_V2[0]:
            tag = Tag()
            with open(filename, "rb") as tag_file:
                found = tag.parse(tag_file, ID3_V2)
                if found:
                    log.debug("Removing ID3 %s tag" %
                              versionToString(tag.version))
                    tag_file.seek(tag.file_info.tag_size)

                    # Open tmp file
                    with tempfile.NamedTemporaryFile("wb", delete=False) \
                            as tmp_file:
                        chunkCopy(tag_file, tmp_file)

                    # Move tmp to orig
                    shutil.copyfile(tmp_file.name, filename)
                    os.unlink(tmp_file.name)

                    retval |= True

        if preserve_file_time and retval and None not in (tag.file_info.atime,
                                                          tag.file_info.mtime):
            tag.file_info.touch((tag.file_info.atime, tag.file_info.mtime))

        return retval

    #------------------------------------------------------------------------------------------#

    @property
    def chapters(self):
        return self._chapters

    @property
    def table_of_contents(self):
        return self._tocs

    @property
    def album_type(self):
        if TXXX_ALBUM_TYPE in self.user_text_frames:
            return self.user_text_frames.get(TXXX_ALBUM_TYPE).text
        else:
            return None

    @album_type.setter
    def album_type(self, t):
        if not t:
            self.user_text_frames.remove(TXXX_ALBUM_TYPE)
        elif t in ALBUM_TYPE_IDS:
            self.user_text_frames.set(t, TXXX_ALBUM_TYPE)
        else:
            raise ValueError("Invalid album_type: %s" % t)

    @property
    def artist_origin(self):
        if TXXX_ARTIST_ORIGIN in self.user_text_frames:
            origin = self.user_text_frames.get(TXXX_ARTIST_ORIGIN).text
            vals = origin.split('\t')
        else:
            vals = [None] * 3

        vals.extend([None] * (3 - len(vals)))
        vals = [None if not v else v for v in vals]
        assert(len(vals) == 3)
        return vals

    @artist_origin.setter
    def artist_origin(self, city, state, country):
        vals = (city, state, country)
        vals = [None if not v else v for v in vals]
        if vals == (None, None, None):
            self.user_text_frames.remove(TXXX_ARTIST_ORIGIN)
        else:
            assert(len(vals) == 3)
            self.user_text_frames.set('\t'.join(vals), TXXX_ARTIST_ORIGIN)
            
    def frameiter(self, fids=None):
        fids = [(b(f, ascii_encode)
            if isinstance(f, str) else f) for f in fids]
        for f in self.frame_set.getAllFrames():
            if f.id in fids:
                yield f