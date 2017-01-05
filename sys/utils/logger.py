import logging

logging.basicConfig()

DEFAULT_FORMAT = '%(name)s:%(levelname)s: %(message)s'
MAIN_LOGGER = "CGInventor"

logging.VERBOSE = logging.DEBUG + 1
logging.addLevelName(logging.VERBOSE, "VERBOSE")

LEVELS = (logging.DEBUG, 
          logging.VERBOSE, 
          logging.INFO,
          logging.WARNING, 
          logging.ERROR, 
          logging.CRITICAL)

#--------------------------------------------------------------------------------------------------#

class Logger(logging.Logger):
    def __init__(self, name):
        logging.Logger.__init__(self, name)

        self.propagate = True
        self.setLevel(logging.NOTSET)


    def verbose(self, msg, *args, **kwargs):
        self.log(logging.VERBOSE, msg, *args, **kwargs)

#--------------------------------------------------------------------------------------------------#

def getLogger(name):
    og_class = logging.getLoggerClass()
    try:
        logging.setLoggerClass(Logger)
        return logging.getLogger(name)
    finally:
        logging.setLoggerClass(og_class)

log = getLogger(MAIN_LOGGER)

#--------------------------------------------------------------------------------------------------#

def initLogging():
    global log

    log.propagate = False

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))
    log.addHandler(console_handler)

    log.setLevel(logging.WARNING)

    return log

