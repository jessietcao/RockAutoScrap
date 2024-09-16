from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
#51823SK

# Configure Selenium (choose your browser, here we use Chrome)
def setup_driver():
    driver = webdriver.Chrome()
    return driver

def search_website(query, driver):
    # Example website - you can change this to your target website
    driver.get("http://catalog.c2cparts.com/")
    time.sleep(2)

    tab = driver.find_element(By.ID, "tab-1150-btnInnerEl")
    tab.click()
    time.sleep(1)

    
    # Find search input and type the query
    search_box = driver.find_element("name", "textfield-1131-inputEl")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    
    # Wait for page to load
    time.sleep(1)  

    partLink= driver.find_element(By.CLASS_NAME, "PartsViewPartNumberLink")
    partLink.click()
    time.sleep(1)

    # Go to the tab with buyer's guide
    #button = driver.find_element(By.XPATH, "//*[contains(text(), 'Buyers Guide')]")
    #button = driver.find_element(By.CSS_SELECTOR, ".x-tab .x-unselectable .x-box-item .x-tab-default .x-top .x-tab-top .x-tab-default-top .x-tab-over")
    #button = driver.find_element(By.XPATH, "//*[contains(@class, 'x-tab') and contains(@class, 'x-unselectable') and contains(@class, 'x-box-item')and contains(@class, 'x-tab-default')and contains(@class, 'x-top')and contains(@class, 'x-tab-top')and contains(@class, 'x-tab-default-top')and contains(@class, 'x-tab-over')]")
    #button.click()
    #time.sleep(1)

    button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//*[text()='Buyers Guide']"))
    )
    button.click()

    # Parse the HTML of the page
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    return soup

def extract_data(soup):
    results = []
    # Find the table or the rows inside the grid
    for row in soup.find_all('tr'):  # Adjust to match the grid's structure
        cells = row.find_all('td')  # Get all cells in the row
        if len(cells) > 0:  # Ensure there are cells in the row
            # Extract data from specific cells
            make = cells[0].text.strip() 
            model = cells[1].text.strip() 
            year = cells[2].text.strip() 
            engine = cells[3].text.strip() 
            carType = cells[4].text.strip() 
            
            results.append({'Make': make, 'Model': model, 'Year': year, 'Engine': engine, 'Type': carType})

    return results

def save_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(f'{filename}.xlsx', index=False)

# Main function to run everything
def main():
    query = input("Enter your search query: ")
    driver = setup_driver()
    
    # Perform search and extract data
    soup = search_website(query, driver)
    data = extract_data(soup)
    
    # Save to Excel
    save_to_excel(data, 'search_results')
    
    driver.quit()
    print(f"Search results saved to search_results.xlsx")

main()
