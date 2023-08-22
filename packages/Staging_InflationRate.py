import pyodbc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# Specify the path to the ChromeDriver executable
webdriver_path = '.\driver\chromedriver.exe'

# Configure the Selenium webdriver
service = Service(webdriver_path)
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run Chrome in headless mode (without opening a browser window)
driver = webdriver.Chrome(service=service, options=options)

# Create a connection to the SQL Server database
conn = pyodbc.connect(
    'Driver={SQL Server};'
    'Server=APU-VM047;'
    'Database=TestDB;'
    'UID=helpdesk;'
    'PWD=Asuult123456;'
)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Open the URL in the webdriver
url = 'https://www.mongolbank.mn/mn/inflation'
driver.get(url)

# Find the table with the ID "inflation-rate-table"
table = driver.find_element(By.ID, 'inflation-rate-table')

# Get the inner HTML content of the table
table_html = table.get_attribute('innerHTML')

# Close the webdriver
driver.quit()

# Process the HTML content using BeautifulSoup
soup = BeautifulSoup(table_html, 'html.parser')

# Find all table rows in the table body
rows = soup.find('tbody').find_all('tr')

# Loop through the rows and insert the new data into the "InflationData" table
for row in rows:
    # Find all table cells in the row
    cells = row.find_all('td')

    # Extract the cell contents
    data = [cell.text.strip() for cell in cells]
    # Check if the data already exists in the "InflationData" table based on the date
    cursor.execute('SELECT COUNT(*) FROM Scrape.InflationData WHERE StatDate = ?', data[0])
    count = cursor.fetchone()[0]

    # Insert the data into the "InflationData" table if it does not exist
    if count == 0:
        cursor.execute('''
            INSERT INTO Scrape.InflationData (StatDate, StateMonthly, StateFromBeginningOfYear, StateYearly, UBMonthly, UBFromBeginningOfYear, UBYearly)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', data)

# Commit the changes to the database
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()
