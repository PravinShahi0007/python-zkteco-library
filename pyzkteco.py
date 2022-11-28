from time import sleep

from . import tables, utils
from .commands import Command
from .const import *




class ZKTeco:
    

    def __init__(self, dev_id, debug=False) -> None:
        self.dev_id = dev_id
        self.debug = debug

    
    def print_package(self, package, dir):
        direction = "Recieved" if dir else "Sent"
        print(f"{direction} bytes: {len(package)}\n\r\t")
        for byte in package:
            print(hex(byte), ' ', end='')
        print("\n\r")

    def send_recieve(self, fd, command: bytes):
        if self.debug:
            self.print_package(command, OUT)

        fd.send(command)
        sleep(TIMEOUT)

        recv_bytes = fd.recv(BUFFER_SIZE)
        if recv_bytes:
            if self.debug:
                self.print_package(recv_bytes, IN)

        return recv_bytes

    def init_connection(self, fd):
        init_cmd = Command.new(self.dev_id, CONNECT_CMD, CONNECTION_P)

        recv_bytes = self.send_recieve(fd, init_cmd)

        if recv_bytes:
            return recv_bytes
        
        return -1
    
    def test_connection(self, fd):
        test_cmd = Command.new(self.dev_id, TEST_CMD, TEST_P)

        recv_bytes = self.send_recieve(fd, test_cmd)

        if recv_bytes:
            return recv_bytes
        
        return -1
    

    
    def clear(self, fd, table: tables.TableSchema):
        payload = bytearray([
            table.id
        ])
        cmd = Command.new(self.dev_id, CLEAR_CMD, payload)

        recv_bytes = self.send_recieve(fd, cmd)

        if recv_bytes:
            return recv_bytes
        
        return -1
    
    def get_table(self, fd, table: tables.TableSchema, fieldname: list | None=None, filter=None, options=None):
        table.apply_fieldname(fieldname)

        payload = bytearray([
            table.id,
            table.column_count 
        ])

        for column in table.column_names:
            payload.append(column.id)

        if options is None: 
            payload.append(0x00)
        else:
            payload.append(len(options))
            payload.append(options[0])

        if filter is None:
            payload.append(0x00)
                
        
        cmd = Command.new(self.dev_id, GET_DEVICE_DATA_CMD, payload)

        recv_bytes = self.send_recieve(fd, cmd)

        if recv_bytes:
            output = utils.parse_table_response(recv_bytes, tableSchema=table)

            return output
        
        return -1
