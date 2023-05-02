# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 19:32:09 2023

@author: MIDINGOYI
"""

import sqlite3
import pypyodbc


types = {"smallint":"Number", "float":"Number", "double":"Number", "bit":"bit", "integer":"Number", "text":"Text", "real":"Number", "timestamp":"Text", "datetime":"datetime"}



def convert(path_to_access_db, path_to_sql_db):
    """
    Converts a Sqlite database to an Access database.
    """
    try:
        
        connection = pypyodbc.win_create_mdb(path_to_access_db)
        cur = connection.cursor()
    
        # Make sqlite connections
        sqlite_connection = sqlite3.connect(path_to_sql_db)
        sqlite_cursor = sqlite_connection.cursor()
        tables = [row[0] for row in sqlite_cursor.execute("SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';")]
    
        for table in tables:
            print(table)
            s = []
            z = []
            columns = [(column[1], column[2]) for column in sqlite_cursor.execute(f"SELECT * FROM PRAGMA_TABLE_INFO('{table}');")]
            for column in columns:
                x = list(column)
                if "varchar" in column[1].lower():  
                    x[1] = "Text"
                elif "counter" in column[1].lower() :
                    x[1] = "Number"
                else:
                    if "(" in column[1] : col =  column[1].split("(")[0]
                    else: col = column[1]
                    x[1] = types[col.lower()]
                column = tuple(x)
                
                if x[0].lower() == "table" or " " in x[0] or "(" in x[0] or "[" in x[0]: x[0] = f"[{x[0]}]"
                z.append(column[1])
                s.append(f"{x[0]} {x[1]}")
            s = ",".join(s)
            print(s)
            cur.execute(f"CREATE TABLE `{table}` ({s});")
            
            rows = [row for row in sqlite_cursor.execute(f"SELECT * FROM `{table}`;")]
            for l,i in enumerate(rows):
                for j, k in enumerate(i):
                    if k=='' and z[j]=="Number":
                        zz = list(rows[l])
                        zz[j]=None
                        rows[l] = tuple(zz)
    
            #rows = [row for row in sqlite_cursor.execute(f"SELECT * FROM {table};")]
    
            try:
                length = len(rows[0])
            except IndexError:
                pass
            else:
                insertion_string = f"insert into `{table}` values "
                insertion_string += "(" + ", ".join(["?" for i in range(length)]) + ")"
                print(insertion_string, "\n")
                cur.executemany(insertion_string, rows)
    
        # close databases
        cur.commit()
        sqlite_connection.close()
        connection.close()
        cur.close()
        
    except sqlite3.Error as e:
        print(f"Error occured: {e}")
        sqlite_connection.close()
        connection.close()
        cur.close()


