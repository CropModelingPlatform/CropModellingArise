# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 10:30:15 2023

@author: MIDINGOYI
"""

import importlib.util

# Specify the file path
file_path = '.../CropModellingArise/scripts/functions/sqlite_to_access.py'

# Specify the module name (without the .py extension)
module_name = 'sqlite_to_access.py'

# Load the module from the file path
spec = importlib.util.spec_from_file_location(module_name, file_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Call the function from the loaded module

path_to_access_db = ".../MasterInput.mdb"
path_to_sql_db = ".../MasterInput.db"
module.convert_sqlite_to_access(path_to_access_db,path_to_sql_db)


#####
path_to_access_db = ".../CelsiusV3nov17_dataArise.mdb"
path_to_sql_db = ".../CelsiusV3nov17_dataArise.db"
module.convert_sqlite_to_access(path_to_access_db,path_to_sql_db)


###### access to sqlite
# Specify the file path
file_path = '.../CropModellingArise/scripts/functions/access_to_sqlite.py'

# Specify the module name (without the .py extension)
module_name = 'access_to_sqlite.py'

# Load the module from the file path
spec = importlib.util.spec_from_file_location(module_name, file_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Call the function from the loaded module

path_to_access_db = ".../MasterInput.accdb"
path_to_sql_db = ".../MasterInput.db"
module.convert_access_to_sqlite(path_to_access_db,path_to_sql_db)


#####
path_to_access_db = ".../CelsiusV3nov17_dataArise.accdb"
path_to_sql_db = ".../CropModellingArise2/CelsiusV3nov17_dataArise.db"
module.convert_access_to_sqlite(path_to_access_db,path_to_sql_db)





# Specify the module name (without the .py extension)
module_name = 'compare_clust_win.py'

# Load the module from the file path
spec = importlib.util.spec_from_file_location(module_name, file_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Call the function from the loaded module

path_to_clust_db = ".../MasterInput_clust.accdb"
path_to_win_db= ".../MasterInput_win.accdb"

plot_rep =".../test"

module.compare_results(path_to_clust_db,path_to_win_db, plot_rep)
