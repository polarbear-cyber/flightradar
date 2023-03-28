import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# connect to the database
conn = sqlite3.connect('flights.db')

# create a table to store the data !IF NOT EXISTS
conn.execute('''CREATE TABLE IF NOT EXISTS flights
                (timestamp INTEGER, flight_hex TEXT, aircraft TEXT)''')

# set up Edge webdriver
driver = webdriver.Edge()

# navigate to the website
driver.get("https://www.flightradar24.com/data/airports/doh/departures")

# wait for the button to be clickable
button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))

# click the button
button.click()

# find all tables on the page
tables = driver.find_elements(By.TAG_NAME, "table")

from msedge.selenium_tools import Edge, EdgeOptions

# Configure Edge webdriver to run in headless mode
options = EdgeOptions()
options.use_chromium = True
options.headless = True

# Set up the Edge webdriver with the specified options
driver2 = Edge(options=options)


def process_table(table):
    # find all rows within the table
    rows = table.find_elements(By.TAG_NAME, "tr")
    ii=0
    # iterate through the rows
    for row in rows:
        # find all table data within the row
        data = row.find_elements(By.TAG_NAME, "td")

        # iterate through the table cells
        for cell in data:
            # find the <a> element with the specified class within the table cell
            link = cell.find_elements(By.CSS_SELECTOR, "a.notranslate.ng-binding")
            
            cell_data = cell.text
            try:
                aircraft = (cell_data.split('\n')[-2])
            except:
                aircraft = None
                # print(cell_data)
            if link:   
                # extract the aircraft data from the <span> element
                    
                driver2.get(link[0].get_attribute("href"))
                
                # wait for the button to be clickable
                if ii==0:
                    button = WebDriverWait(driver2, 3).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
                    # click the button
                    button.click()
                    # time.sleep(5)
                    ii=1
                # find all tables on the second page
                second_page_tables = driver2.find_elements(By.TAG_NAME, "table")
        
                # iterate through the second page tables
                for second_page_table in second_page_tables:
                    # find the <a> element with the specified class within the table
                    playback_button = second_page_table.find_elements(By.CSS_SELECTOR, "a.btn.btn-sm.btn-playback.btn-table-action.text-white.bkg-blue.fs-10")
                    
                    for i in playback_button:
                        # get data-timestamp and data-flight-hex attributes and append them to the list
                        try:
                            timestamp = i.get_attribute("data-timestamp")
                            flight_hex = i.get_attribute("data-flight-hex")
                            # insert the data into the database
                            if len(flight_hex)<4:
                                pass
                            else:                                
                                conn.execute("INSERT INTO flights (timestamp, flight_hex, aircraft) VALUES (?, ?, ?)", (timestamp, flight_hex, aircraft))
                                conn.commit()
                                print((timestamp, flight_hex, aircraft))
                        except:
                            pass

while True:
    # find all tables on the page
    tables = WebDriverWait(driver, 1).until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))

    if not tables:
        break

    # process the first table and then remove it from the list of tables
    process_table(tables.pop(0))

# close the database connection
conn.close()
