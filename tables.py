from collections import namedtuple


column = namedtuple('column', 'id name')
filter = namedtuple('filter', 'columns')

class TableSchema:
    def __init__(self, id, name, columns) -> None:
        self.id = id
        self.name = name
        self.column_names = []
        for i, _name in enumerate(columns):
                self.column_names.append(column(i + 1, _name))

        self.column_count = len(self.column_names)

    def apply_fieldname(self, filter):
        if filter is None:
            return
        new_column_names = []
        for _column in self.column_names:
            if _column.name in filter.columns:
                new_column_names.append(_column)
        
        self.column_count = len(new_column_names)
        self.column_names = new_column_names
        
    

def fieldnames(columns: str | list[str]):
    if columns == '*' or len(columns) == 0:
        return None
    
    fltr = filter(columns=columns)
    return fltr

def Users():
    return TableSchema(1, 'user', ['CardNo', 'Pin', 'Password', 'Group', 'StartTime', 'EndTime', '?'])

def Transactions():
    return TableSchema(5, 'transaction', ['CardNo', 'Pin', 'Verified', 'DoorID', 'EventType', 'InOutState', 'Time_second'])
