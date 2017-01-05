import os, mimetypes, time

#--------------------------------------------------------------------------------------------------#

mime_types = mimetypes.MimeTypes()
del mimetypes

#--------------------------------------------------------------------------------------------------#

def guessMimetype(file_name, with_encoding=False):
    mime, enc = mime_types.guess_type(file_name, strict=False)
    return mime if not with_encoding else (mime, enc)