from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

# Setting up Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Optional: run in headless mode
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Navigate to the main listings webpage
url = 'https://www.royallepage.ca/en/'
driver.get(url)
time.sleep(5)  # Wait for the page to load completely

# Extract the main page source and parse with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Find the listings on the page
listings = soup.find_all('li', {'class': lambda value: value and value.startswith('card-group__item item')})

# List to hold extracted data
data = []

# Loop through each listing and extract main data
for listing in listings:
    try:
        # Extract main page data
        listing_id = listing.find('div', class_='card card--listing-card js-listing js-property-details').get("data-id", "N/A")
        housetype = listing.find('span', class_='listing-flag__text')
        housetype = housetype.get_text(strip=True) if housetype else "HouseType not Given"
        type_spans = listing.find('div', class_='listing-meta listing-meta--small').find_all('span') if listing.find('div', class_='listing-meta listing-meta--small') else []
        type_ = ", ".join([span.get_text(strip=True) for span in type_spans]) if type_spans else "Type Not Given"
        type_ = re.sub(r'[0-9,]', '', type_).strip()
        price = listing.find('span', class_='price').get_text(strip=True) if listing.find('span', class_='price') else "Price Not Given"
        address1 = listing.find('address', class_='address-1').get_text(strip=True) if listing.find('address', class_='address-1') else "Address1 Not Given"
        address2 = listing.find('address', class_='card__address-2').get_text(strip=True) if listing.find('address', class_='card__address-2') else "Address2 Not Given"
        
        # Extract listing link
        link_tag = listing.find('a', href=True)
        link = link_tag.get('href', 'Link Not Available') if link_tag else "Link Not Available"
        if link.startswith('//'):
            link = 'https:' + link
        elif link.startswith('/'):
            link = 'https://www.royallepage.ca' + link

        # Navigate to individual listing page to extract more details
        driver.get(link)
        time.sleep(3)  # Wait for the page to load completely
        individual_soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract square feet
        building_features = individual_soup.find('div', class_='details-row')
        if building_features:
            sqft_element = building_features.find('span', string="Floor Space:")
            sqft = sqft_element.find_next('span', class_='value').get_text(strip=True) if sqft_element else "Square Feet Not Given"
        else:
            sqft = "Square Feet Not Given"
            
        '''# Look within the `details-row` div for Floor Space info
        if building_features:
        # Attempt to locate the specific 'li' containing 'Floor Space'
            floor_space_li = building_features.find('li', string=lambda text: 'Floor Space' in text if text else False)
        if floor_space_li:
            sqft_value = floor_space_li.find('span', class_='value')
            sqft = sqft_value.get_text(strip=True) if sqft_value else sqft'''


        # Extract beds
        beds_element = individual_soup.find('div', class_='bed-bath-box__item beds')
        beds = beds_element.get_text(strip=True) if beds_element else "Beds Not Given"

        # Extract baths
        baths_element = individual_soup.find('div', class_='bed-bath-box__item baths')
        baths = baths_element.get_text(strip=True) if baths_element else "Baths Not Given"

        # Extract listing date if available
        date_element = individual_soup.find('span', class_='listing-date')
        date = date_element.get_text(strip=True) if date_element else "Date Not Given"

        # Print or store extracted data
        print(f"Listing ID: {listing_id}")
        print(f"HouseType: {housetype}")
        print(f"Type: {type_}")
        print(f"Price: {price}")
        print(f"Address1: {address1}")
        print(f"Address2: {address2}")
        print(f"Link: {link}")
        print(f"Square Feet: {sqft}")
        print(f"Beds: {beds}")
        print(f"Baths: {baths}")
        print(f"Date: {date}")
        print('-' * 50)

        # Append to data list
        data.append({
            "Listing ID": listing_id,
            "HouseType": housetype,
            "Type": type_,
            "Price": price,
            "Address1": address1,
            "Address2": address2,
            "Link": link,
            "Square Feet": sqft,
            "Beds": beds,
            "Baths": baths,
            "Date": date
        })

    except AttributeError:
        continue

# Close the driver
driver.quit()

# Save data to CSV
df = pd.DataFrame(data)
df.to_csv('royal_lepage_listings.csv', index=False)
print("Data successfully saved to royal_lepage_listings.csv")
