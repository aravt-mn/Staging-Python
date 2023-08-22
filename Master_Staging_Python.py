import pyodbc
import importlib.util
import os
from datetime import date

# Define the connection string for your MSSQL database
server = 'APU-VM047'
database = 'MetadataDB'
username = 'helpdesk'
password = 'Asuult123456'
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# Establish a connection to the database
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# Define a function to load the packages based on the configuration
def load_packages():
    # Query the database for the list of activated packages from the PackageData table
    cursor.execute("SELECT package_name FROM PackageData WHERE BATCH_NAME = 'Python' AND PACKAGE_ACTIVE = 1")
    activated_packages = cursor.fetchall()

    # For each activated package, load the corresponding package file
    for package in activated_packages:
        package_name = package[0]
        package_path = f'.C:\Users\DELL LATITUDE E7470\Documents\github\Staging-Python\packages\{package_name}.py'

        # Ensure that the package file exists
        if os.path.exists(package_path):
            # Load the package module dynamically
            spec = importlib.util.spec_from_file_location(package_name, package_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f'Loaded package: {package_name}')
            
            datetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            
            cursor.execute("SELECT BATCH_NAME, PACKAGE_NAME FROM PackageData WHERE BATCH_NAME = 'Python' AND PACKAGE_ACTIVE = 1")
            package_data = cursor.fetchall()
            
            
            cursor.execute('''
                           INSERT INTO [dbo].[BatchLog] (BATCH_NAME, LOAD_STATUS, LOAD_START_DATETIME)
                           VALUES (?, 'Started', ?);
                           SELECT SCOPE_IDENTITY() AS LastLogId;
                           ''', package_data[0], datetime)
            
            cursor.execute("SELECT BATCH_LOG_ID FROM BatchLog WHERE BATCH_NAME='Python' AND LOAD_START_DATETIME = ? AND PACKAGE_ACTIVE = 1",datetime)
            package_data.insert(cursor.fetchall())
            
            cursor.execute('''
                           INSERT INTO [dbo].[PackageLog] (BATCH_NAME, PACKAGE_NAME, BATCH_LOG_ID, LOAD_START_DATETIME, LOAD_STATUS)
                           VALUES (?, ?, ?, ?, 'Started');
                           SELECT SCOPE_IDENTITY() AS LastLogId;
                           ''', package_data, datetime)
            
        else:
            print(f'Package file not found for {package_name}')

# Call the function to load the packages based on the configuration
load_packages()

# Close the database connection
conn.close()