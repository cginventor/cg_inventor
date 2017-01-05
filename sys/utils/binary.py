from cg_inventor.sys.utils import version

python_version = version.getPythonVersion()
python2 = python_version[0] == 2
python3 = python_version[0] == 3

BYTES_TYPE = str if python2 else bytes

#--------------------------------------------------------------------------------------------------# 

def toByteString(n):
    if python2:
        return chr(n)
    else:
        return((n,))

#--------------------------------------------------------------------------------------------------# 

def byteIterator(bites):
    assert(isinstance(bites, str if python2 else bytes))
    for b in bites:
        yield b if python2 else bytes((b,))
        
#--------------------------------------------------------------------------------------------------# 

def bytes2bin(bytes, size=8):
    if size < 1 or size > 8:
        raise ValueError("Invalid size value: %d." %size)
    
    return_value = []
    for b in byteIterator(bytes):
        bits = []
        b = ord(b)
        while b > 0:
            bits.append(b & 1)
            b >>= 1
        
        if len(bits) < size:
            bits.extend([0] * (size - len(bits)))
        elif len(bits) > size:
            bits = bits[:size]
        
        bits.reverse()
        return_value.extend(bits)
    
    return return_value

#--------------------------------------------------------------------------------------------------# 

def bin2bytes(x):
    bits = []
    bits.extend(x)
    bits.reverse()

    i = 0
    out = b''
    multi = 1
    ttl = 0
    for b in bits:
        i += 1
        ttl += b * multi
        multi *= 2
        if i == 8:
            i = 0
            out += toByteString(ttl)
            multi = 1
            ttl = 0

    if multi > 1:
        out += toByteString(ttl)

    out = bytearray(out)
    out.reverse()
    out = BYTES_TYPE(out)
    return out

#--------------------------------------------------------------------------------------------------# 

def bin2dec(x):
    bits = []
    bits.extend(x)
    bits.reverse()

    multi = 1
    value = 0
    for b in bits:
        value += b * multi
        multi *= 2
    return value

#--------------------------------------------------------------------------------------------------# 

def bytes2dec(bytes, sz=8):
    return bin2dec(bytes2bin(bytes, sz))

#--------------------------------------------------------------------------------------------------#

def dec2bin(n, p=1):
    assert(n >= 0)
    return_value = []

    while n > 0:
        return_value.append(n & 1)
        n >>= 1

    if p > 0:
        return_value.extend([0] * (p - len(return_value)))
    return_value.reverse()
    return return_value

#--------------------------------------------------------------------------------------------------#

def dec2bytes(n, p=1):
    return bin2bytes(dec2bin(n, p))

#--------------------------------------------------------------------------------------------------#

def bin2synchsafe(x):
    n = bin2dec(x)
    if len(x) > 32 or n > 268435456:
        raise ValueError("Invalid value: %s." % str(x))
    elif len(x) < 8:
        return x

    bites = b""
    bites += toByteString((n >> 21) & 0x7f)
    bites += toByteString((n >> 14) & 0x7f)
    bites += toByteString((n >>  7) & 0x7f)
    bites += toByteString((n >>  0) & 0x7f)
    bits = bytes2bin(bites)
    assert(len(bits) == 32)

    return bits
        