import libscrc


def computeCRC(data):
    crc = libscrc.ibm(data)
    return crc