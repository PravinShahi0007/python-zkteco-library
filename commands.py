import struct
from . import crc16


class Command:
    def new(dev_id, command_id, payload) -> bytes:
        data_for_crc  = struct.pack(f"B B H {len(payload)}B", dev_id, command_id, len(payload), *payload)
        crc = crc16.computeCRC(data_for_crc)

        data = struct.pack(f"<B B B H {len(payload)}B H B", 0xaa, dev_id, command_id, len(payload), *payload, crc, 0x55)
        return data

    