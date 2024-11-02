from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

# Initialize the Selenium WebDriver
driver = webdriver.Chrome()  # Specify the path to ChromeDriver if necessary
url = 'https://www.zolo.ca/index.php?sarea=&s='

# Open the URL
driver.get(url)

# Wait for the page to fully load
time.sleep(5)

# Extract listings using XPath
listings = driver.find_elements(By.XPATH, "//li[contains(@data-testid, 'listing-card-list-item')]")

# Parse the page with BeautifulSoup (optional if you prefer parsing with Selenium)
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Initialize a counter
i = 0

# Loop through each listing
for listing in listings:
    i += 1
    try:
        # Listing ID
        listing_id = listing.find_element(By.XPATH, ".//section[@data-testid='listing-card']").get_attribute('data-listingid')
        
        # Title
        title = listing.find_element(By.XPATH, ".//a[@data-testid='listing-link']").text.strip()
        
        # Price
        price = listing.find_element(By.XPATH, ".//p[@data-testid='listing-price']").text.strip()
        
        # Location
        location = listing.find_element(By.XPATH, ".//p[@data-testid='listing-location']").text.strip()
        
        # Link
        link = listing.find_element(By.XPATH, ".//a[@data-testid='listing-link']").get_attribute('href')
        
        # Description
        description = listing.find_element(By.XPATH, ".//p[@data-testid='listing-description']").text.strip()

        # Output the extracted data
        print(f"Listing ID: {listing_id}")
        print(f"Title: {title}")
        print(f"Price: {price}")
        print(f"Location: {location}")
        print(f"Link: {link}")
        print(f"Description: {description}")
        print('-' * 50)
        
    except Exception as e:
        print(f"Error: {e}")
        continue

print(f"Total listings found: {i}")
driver.quit()
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)  # wait up to 10 seconds
listings = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@data-testid, 'listing-card-list-item')]")))
