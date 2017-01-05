import sys, locale
import core; reload(core)
from .core import load

#--------------------------------------------------------------------------------------------------#

class Error(Exception):
    def __init__(self, *args):
        super(Error, self).__init__(*args)
        if args:
            self.message = args[0]

#--------------------------------------------------------------------------------------------------#

del sys, locale
