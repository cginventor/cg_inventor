import sys

def getPythonVersion():
    major, minor, micro, release_level, serial = sys.version_info
    return (major, minor, micro)