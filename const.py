OUT = 0
IN = 1

TIMEOUT = 1

BUFFER_SIZE = 4 * 1024 * 1024
BYTE_ORDER = 'little'

# Commands
GET_DEVICE_DATA_CMD = 0x08
CONNECT_CMD = 0x76
TEST_CMD = 0x01
CLEAR_CMD = 0x19

# Options
NO_OPT = []
NEWRECORD = [0x01]

# Payloads
CONNECTION_P = bytearray([0x00, 0x00, 0x01, 0x00])
TEST_P = bytearray([])