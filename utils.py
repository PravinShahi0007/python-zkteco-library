from .const import BYTE_ORDER

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

from . import tables
def parse_table_response(data: bytes, tableSchema: tables.TableSchema):
    # Get response payload
    # first 5 bytes reserved for header and last 3 bytes are CRC and end byte
    payload = data[5:-3]

    data = payload[tableSchema.column_count + 1 + 1:]
    output = []

    values = transale_2d(data, tableSchema.column_count)

    for row in values:
        item = {}
        for i, value in enumerate(row):
            item[tableSchema.column_names[i].name] = value
        output.append(item)

    return output