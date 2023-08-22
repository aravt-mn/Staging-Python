import pyodbc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# Specify the path to the ChromeDriver executable
webdriver_path = 'C:\Program Files\driver\chromedriver.exe'

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
url = 'https://www.mongolbank.mn/mn/forex-auction'
driver.get(url)

# Find the table with the ID "dataTable1"
table = driver.find_element(By.ID, 'dataTable1')

# Get the inner HTML content of the table
table_html = table.get_attribute('outerHTML')

# Close the webdriver
driver.quit()

# Process the HTML content using BeautifulSoup
soup = BeautifulSoup(table_html, 'html.parser')

# Find all table rows in the table body
rows = soup.find('tbody').find_all('tr')

# Loop through the rows and insert the new data into the "ForexAuctionData" table
for row in rows:
    # Find all table cells in the row
    cells = row.find_all('td')

    # Extract the cell contents
    data = [cell.text.strip() for cell in cells]
    data[1] = data[1].replace(',','')
    data[1] = data[1].replace('-','')
    data[2] = data[2].replace(',','')
    data[2] = data[2].replace('-','')
    data_with_null = [None if value == '' else value for value in data]
    # Check if the data already exists in the "ForexAuctionData" table based on the date
    cursor.execute('SELECT COUNT(*) FROM Scrape.ForexAuctionData WHERE StatDate = ?', data[0])
    count = cursor.fetchone()[0]

    # Insert the data into the "ForexAuctionData" table if it does not exist
    if count == 0:
        cursor.execute('''
            INSERT INTO  Scrape.ForexAuctionData (StatDate, ToBuy, ToSell, CommercialForm, Detail)
            VALUES (?, ?, ?, ?, ?)
        ''', data_with_null)

# Commit the changes to the database
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()
