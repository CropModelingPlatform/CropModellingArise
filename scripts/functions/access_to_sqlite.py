import pyodbc
import sqlite3
from path import Path

def convert_access_to_sqlite(path_to_access_db, path_to_sql_db):
    """
    Converts an Access database to a SQLite database.
    """
    # Make sqlite connections
    sqlite_conn = sqlite3.connect(path_to_sql_db)
    sqlite_cursor = sqlite_conn.cursor()
 
    # Make mdb connections
    constr = "DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={0};".format(Path(path_to_access_db))
    access_conn = pyodbc.connect(constr, autocommit=False)
    
    
    prev_converter = access_conn.get_output_converter(pyodbc.SQL_WVARCHAR)
    access_conn.add_output_converter(pyodbc.SQL_WVARCHAR, decode_sketchy_utf16)

    cursor = access_conn.cursor()
    
    tables = [table_info.table_name for table_info in cursor.tables(tableType='TABLE')]
 
    for table in tables:
        # Access databases, have several internal tables. They all start with the
        # "MSys" prefix. If you need them, just remove the if clause.
        if not table.startswith("MSys"):
            print(table)
            ## Create tables
            columns = [column for column in cursor.columns(table=table)]
            access_conn.add_output_converter(pyodbc.SQL_WVARCHAR, prev_converter)

            s = []

            for column in columns:
                # Quoting table names with braces.
                s.append("%s %s(%s)" % ("[" + column.column_name + "]",
                                        column.type_name,
                                        column.column_size))
            creation_string = ("CREATE TABLE [%s] (\n" % table +
                               ",\n".join(s) +
                               "\n);")
            sqlite_cursor.execute(creation_string)
 
            ## Insert values
            # select everything from the mdb-table
            rows = [row for row in cursor.execute("SELECT * FROM [%s];" % table)]
            # Check if the table has data. If it doesn't go to the next table, else
            # insert them to the sqlite database.
            try:
                length = len(rows[0])
            except IndexError:
                pass
            else:
                insertion_string = "insert into [%s] values " % table
                insertion_string += "(" + ", ".join(["?" for i in range(length)]) + ")"
                sqlite_conn.executemany(insertion_string, rows)
    
    # close databases
    sqlite_conn.commit()
    sqlite_conn.close()
    access_conn.close()
 
    