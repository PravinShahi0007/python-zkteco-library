import socket
from time import sleep
import struct
from collections import namedtuple
from ctypes import c_byte, c_uint16

OUT = 0
IN = 1
TIMEOUT = 1
BUFFER_SIZE = 4 * 1024 * 1024
BYTE_ORDER = 'little'

class Options:
    NO_OPT = []
    NEWRECORD = [0x01]

class Tables:
    column = namedtuple('column', 'name id')
    USER = {
        "id": 0x01,
        "column_count": 0x07,
        "column_names": [column('CardNo', 0x01), column('Pin', 0x02), column('Password', 0x03), column('Group', 0x04), column('StartTime', 0x05), column('EndTime', 0x06), column('?', 0x07)]
    }
    TRANSACTION = {
        "id": 0x05,
        "column_count": 0x07,
        "column_names": [column('CardNo', 0x01), column('Pin', 0x02), column('Verified', 0x03), column('DoorID', 0x04), column('EventType', 0x05), column('InOutState', 0x06), column('Time_second', 0x07)]
    }

class Commands:
    GET_DEVICE_DATA = 0x08
    CONNECT = 0x76
    TEST = 0x01

class Payloads:
    CONNECTION = bytearray([0x00, 0x00, 0x01, 0x00])
    TEST = bytearray([])

class CRC:
    GET_ALL_USERS = 0xe1a4
    GET_NEW_TRANSACTIONS = 0xe347



def transale_2d(payload: bytes, values_in_row: int) -> list[list]:
    """
    Translate ZKTeco response data into 2-d array
    with values in row specified amount
    [[...], ..., [...]]
    """
    rows = []
    row = []
    size = -1
    i = 0
    while i < len(payload):
        # first byte of column is size of cell data
        size = payload[i]
        # if cell size is 0, no additional byte for cell data supplied, so must set it manually
        value = 0
        # cell value begins at next byte after size byte
        start_cell_byte = i + 1
        # cell value end at start_cell_byte + size of cell, must add 1 to ensure all bytes inside the region
        end_cell_byte = i + size + 1

        if size != 0:
            # convert bytes region to integer with little endian ordering
            value = int.from_bytes(payload[start_cell_byte : end_cell_byte], BYTE_ORDER)

        # append value to row
        row.append(value)

        # Set i to end cell byte index
        i = end_cell_byte

        # Check if row length equal to how many values there need to be, append and reset if true
        if len(row) == values_in_row:
            rows.append(row)
            row = []

    return rows

def Command(dev_id, command_id, payload, CRC):
    fmt = f"<B B B H {len(payload)}B H B"
    data = struct.pack(fmt, 0xaa, dev_id, command_id, len(payload), *payload, CRC, 0x55)
    return data



class ZKTeco:
    

    def __init__(self, dev_id) -> None:
        self.dev_id = dev_id
    
    def print_package(self, package, dir):
        direction = "Recieved" if dir else "Sent"
        print(f"{direction} bytes: {len(package)}\n\r\t")
        for byte in package:
            print(hex(byte), ' ', end='')
        print("\n\r")

    def send_recieve(self, fd: socket.socket, command: Command):
        self.print_package(command, OUT)

        fd.send(command)
        sleep(TIMEOUT)

        recv_bytes = fd.recv(BUFFER_SIZE)
        if recv_bytes:
            self.print_package(recv_bytes, IN)

        return recv_bytes

    def init_connection(self, fd):
        init_cmd = Command(self.dev_id, Commands.CONNECT, Payloads.CONNECTION, 0x1fd6)

        recv_bytes = self.send_recieve(fd, init_cmd)

        if recv_bytes:
            return recv_bytes
        
        return -1
    
    def test_connection(self, fd):
        test_cmd = Command(self.dev_id, Commands.TEST, Payloads.TEST, 0x3c50)

        recv_bytes = self.send_recieve(fd, test_cmd)

        if recv_bytes:
            return recv_bytes
        
        return -1
    
    def decode(_bytes):
        pass

    
    
    def get_table(self, fd, table: dict, fieldname: list=None, filter=None, options=None, CRC=None):
        if CRC is None:
            raise Exception('CRC cannot be calculated implicitly yer')

        payload = bytearray([
            table['id'],         
        ])

        if fieldname is None:
            payload.append(table['column_count'])
        else:
            payload.append(len(fieldname))
        
        columns = []
        for column in table['column_names']:
            if fieldname is None:
                payload.append(column[1])
                columns.append(column[1])
                continue
            if column[0] in fieldname:
                payload.append(column[1])
                columns.append(column[1])

        if options is None: 
            payload.append(0x00)
        else:
            payload.append(len(options))
            payload.append(options[0])

        if filter is None:
            payload.append(0x00)
                
        
        #TODO Find out how to calculate CRC

        cmd = Command(self.dev_id, Commands.GET_DEVICE_DATA, payload, CRC) ##  0xe1a4

        recv_bytes = self.send_recieve(fd, cmd)


        

        # Get response payload
        # first 5 bytes reserved for header and last 3 bytes are CRC and end byte
        payload = recv_bytes[5:-3]

        data = payload[len(columns) + 1 + 1:]
        output = []

        values = transale_2d(data, table['column_count'])

        for row in values:
            item = {}
            for i, value in enumerate(row):
                item[table['column_names'][i].name] = value
            output.append(item)

        


        
        # self.print_package(data, IN)
        print(output)
        # for i in range(payload_size)
        # data = struct.unpack()


        if recv_bytes:
            return recv_bytes
        
        return -1



if __name__ == "__main__":
    zk = ZKTeco(0x01)
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.connect(('172.16.222.170', 4370))

    zk.init_connection(skt)
    zk.test_connection(skt)
    zk.get_table(skt, Tables.USER, CRC=CRC.GET_ALL_USERS)
    zk.get_table(skt, Tables.TRANSACTION, options=Options.NEWRECORD, CRC=CRC.GET_NEW_TRANSACTIONS)
