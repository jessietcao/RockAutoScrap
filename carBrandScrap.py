from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import mysql.connector
#51823SK

# Function to connect to the database
def connect_db(database_name):
    return mysql.connector.connect(
        host='localhost',       # e.g., 'localhost'
        user='root',
        password='',
        database=database_name
    )

def get_number_by_car_model(car_model):
    db = connect_db("vcdb")
    cursor = db.cursor()

    # SQL query using two schemas
    # query = """
    #     SELECT schema2.some_table.some_number
    #     FROM schema1.cars
    #     JOIN schema2.some_table ON schema1.cars.country = schema2.some_table.country
    #     WHERE schema1.cars.model = %s
    #"""

    query = """
        SELECT MakeID 
        FROM vcdb.make WHERE vcdb.make.MakeName = %s

    """
    cursor.execute(query, (car_model,))
    result = cursor.fetchone()
    
    db.close()
    
    if result:
        return result[0]  
    else:
        print(car_model + " failed to retrieve model ID")
        return None

def get_number_by_region(region_name):
    db = connect_db("autoapp")
    cursor = db.cursor()

    query = """
        SELECT regionid
        FROM autoapp.region WHERE autoapp.region.regionabbr = %s OR autoapp.region.regionname = %s
    """
    cursor.execute(query, (region_name, region_name,))
    result = cursor.fetchone()
    
    db.close()
    
    if result:
        return result[0]  
    elif region_name == "South Korea":
        return 6 #South Korea is Korea in database
    else:
        return 4 #assume the country is "European"

# Configure Selenium (choose your browser, here we use Chrome)
def setup_driver():
    driver = webdriver.Chrome()
    return driver

def search_website(query, driver):
    # Example website - you can change this to your target website
    driver.get("https://www.car.info/en-se/brands")
    time.sleep(2)

        
    # Find search input and type the query
    search_box = driver.find_element(By.ID, "brand_search")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    
    # Wait for page to load
    time.sleep(1)  

    try:
        partLink= driver.find_element(By.CLASS_NAME, "brand_name")
        partLink.click()
        time.sleep(1)
    except:
        print("Empty results: " + query)
        return None
    
    # Go to the tab with buyer's guide
    #button = driver.find_element(By.XPATH, "//*[contains(text(), 'Buyers Guide')]")
    #button = driver.find_element(By.CSS_SELECTOR, ".x-tab .x-unselectable .x-box-item .x-tab-default .x-top .x-tab-top .x-tab-default-top .x-tab-over")
    #button = driver.find_element(By.XPATH, "//*[contains(@class, 'x-tab') and contains(@class, 'x-unselectable') and contains(@class, 'x-box-item')and contains(@class, 'x-tab-default')and contains(@class, 'x-top')and contains(@class, 'x-tab-top')and contains(@class, 'x-tab-default-top')and contains(@class, 'x-tab-over')]")
    #button.click()
    #time.sleep(1)
    # Parse the HTML of the page
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    return soup

def extract_data(query, soup):
    # Find the table or the rows inside the grid
    if (soup != None):
        cells = soup.find_all(class_='ast-i')
    
        country = cells[2].text.strip() 

        regionID = get_number_by_region(country)
        makeID =  get_number_by_car_model(query)

        db = connect_db("backpack")
        cursor = db.cursor()

        try:
            # Insert data into the table
            insert_query = """
                INSERT INTO backpack.make_to_region
                VALUES (%s, %s);
            """
            cursor.execute(insert_query, (makeID, regionID))

            # Commit the transaction
            db.commit()

            # Check if the insert was successful
            if cursor.rowcount > 0:
                print("Data inserted successfully")
            else:
                print("Insert failed")

        except Exception as e:
            db.rollback()  # Rollback in case of error
            print(f"An error occurred: {e}")

        finally:
            cursor.close()  # Close the cursor
            db.close()  # Close the database connection



# Main function to run everything
def main():
    '''
    query = input("Enter your search query: ")
    driver = setup_driver()
    
    # Perform search and extract data
    soup = search_website(query, driver)
    data = extract_data(query, soup)
    
    # Save to Excel
    #name = input("Enter excel name: ")
    name = query + "info"+"single"
    save_to_excel(data, name)

    '''
    print("Enter your search queries (press Enter on an empty line to finish):")
    
    queries = []
    while True:
        query = input()
        if query.strip() == "":
            break
        queries.append(query.strip())
    
    if not queries:
        print("No queries entered.")
        return

    driver = setup_driver()
    
    for query in queries:
        # Perform search and extract data 
        soup = search_website(query, driver)
        extract_data(query, soup)
        
    driver.quit()


main()
