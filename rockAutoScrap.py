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
    driver.get("https://www.rockauto.com/en/partsearch/")
    time.sleep(2)

        
    # Find search input and type the query
    search_box = driver.find_element("name", "partsearch[partnum][partsearch_007]")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    
    # Wait for page to load
    time.sleep(1)  

    try:
        partLink= driver.find_element(By.CLASS_NAME, "listing-final-partnumber")
        partLink.click()
        time.sleep(1)
    except:
        print("Empty results: " + query)

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
    results = []
    # Find the table or the rows inside the grid
    for row in soup.find_all('tr'):  # Adjust to match the grid's structure
        cells = row.find_all('td')  # Get all cells in the row
        if len(cells) >= 3:  # Ensure there are cells in the row
            # Extract data from specific cells
            make = cells[0].text.strip() 
            model = cells[1].text.strip() 
            if (model == "ALL THE PARTS YOUR CAR WILL EVER NEED" ):
                break
            year = cells[2].text.strip() 
            if (len(year) > 4):
                start = year[:4]
                end = year[5:]
            else:
                start = year
                end = year
            
            results.append({'BOSDA#': query, 'Make': make, 'Model': model, 'Start': start, 'End': end})

    return results

def save_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(f'{filename}.xlsx', index=False)

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
    name = query + "info"
    save_to_excel(data, name)


    print("Enter your search queries (press Enter on an empty line to finish):")
    '''
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
    
    soup = search_website(query, driver)
    data = extract_data(queries[0], soup)
    for query in queries:
        # Perform search and extract data
        if (query != queries[0]): 
            soup = search_website(query, driver)
            new_data = extract_data(query, soup)
            data += new_data  # Combine data from each query
    
    # Save to Excel
    #name = input("Enter excel name: ")
    name = queries[0] + "info"
    save_to_excel(data, name)
    
    
    #driver.quit()
    print(f"Search results saved to " + name)

main()
