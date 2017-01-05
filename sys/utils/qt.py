import PyQt4.QtCore as qc
import PyQt4.QtGui as qg

# image conversion types
#
BRIGHTNESS = 1
CONTRAST   = 2
GAMMA      = 3

#--------------------------------------------------------------------------------------------------#

def recurseHierarchy(widget, tab=''):
    if not isinstance(widget, qc.QObject):
        raise TypeError('Non QObject received.')

    tab += '    '
    for child in widget.children():
        recurseHierarchy(child, tab)

#--------------------------------------------------------------------------------------------------#                
        
def _generateLookupTable(value, lookupType):
    if lookupType not in [BRIGHTNESS, CONTRAST, GAMMA]:
        raise TypeError('Lookup type not recognised.')
    
    lookup = range(256)
    
    if lookupType == BRIGHTNESS:
        for index in range(256):
            lookup[index] = max(min(255, (index + (value * 255 / 100))), 0)
    if lookupType == CONTRAST:
        for index in range(256):
            lookup[index] = max(min(255, int(((index - 127) * (value / 100.0) + 127))), 0)
    if lookupType == GAMMA:
        for index in range(256):
            lookup[index] = max(min(255, int(pow(index / 255.0, 100.0 / value) * 255)), 0)
            
    return lookup

#--------------------------------------------------------------------------------------------------#

def changeImage(image, lookup):
    if not isinstance(image, qg.QImage):
        raise TypeError('Non QImage received.')
    
    import struct
    
    if image.format() != qg.QImage.Format_RGB32:
        image.convertToFormat(qg.QImage.Format_RGB32)
        
    colors = image.colorTable()    
    linebytes = image.width() *  4
    
    if not len(colors):    
        if image.hasAlphaChannel():
            for y in range(image.height()):
                line = image.scanLine(y).asstring(linebytes)
                for x in xrange(image.width()):
                    color = struct.unpack('I', line[x*4:x*4+4])[0]
                    if color == 0: continue
                    red   = lookup[qg.qRed(color)]
                    green = lookup[qg.qGreen(color)]
                    blue  = lookup[qg.qBlue(color)]
                    alpha = lookup[qg.qAlpha(color)]
                    image.setPixel(x, y, qg.qRgba(red, green, blue, alpha))
        else:
            for y in range(image.height()):
                line = image.scanLine(y)
                for x in range(image.width()):
                    red   = lookup[line[x].red()]
                    green = lookup[line[x].green()]
                    blue  = lookup[line[x].blue()]
                    line[x] = qg.QRgb(red, green, blue, alpha)
    else:
        for color in colors:
            red   = lookup[color.red()]
            green = lookup[color.green()]
            blue  = lookup[color.blue()]
            colors[i] = qg.QRgb(red, green, blue)
            
    return image

#--------------------------------------------------------------------------------------------------#

def changeBrightness(image, value):
    lookup = _generateLookupTable(value, BRIGHTNESS)
    return changeImage(image, lookup)


def changeContrast(image, value):
    lookup = _generateLookupTable(value, CONTRAST)
    return changeImage(image, lookup)


def changeGamma(image, value):
    lookup = _generateLookupTable(value, GAMMA)
    return changeImage(image, lookup)

#--------------------------------------------------------------------------------------------------#