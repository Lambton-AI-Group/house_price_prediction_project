from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

# Setting up Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Optional: run in headless mode
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Navigate to the webpage
url = 'https://www.royallepage.ca/en/'
driver.get(url)
time.sleep(5)  # Wait for the page to load completely

# Extract the page source and parse with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Close the driver as it's no longer needed
driver.quit()

# Finding the listings on the page
listings = soup.find_all('li', {'class': lambda value: value and value.startswith('card-group__item item')})

# List to hold extracted data
data = []

# Loop through each listing and extract data
for listing in listings:
    try:
        # Extract data from each listing
        listing_id = listing.get('data-id', 'N/A')
        housetype = listing.find('span', class_='listing-flag__text').get_text(strip=True) if listing.find('span', class_='listing-flag__text') else "House Type not Given"
        type_ = listing.find('span', class_='listing-meta').get_text(strip=True) if listing.find('span', class_='listing-meta') else "Type Not Given"
        price = listing.find('span', class_='price').get_text(strip=True) if listing.find('span', class_='price') else "Price Not Given"
        address1 = listing.find('address', class_='address-1').get_text(strip=True) if listing.find('address', class_='address-1') else "Address1 Not Given"
        address2 = listing.find('address', class_='card__address-2').get_text(strip=True) if listing.find('address', class_='card__address-2') else "Address2 Not Given"
        #link = listing.find('a', class_='card__media')['href'] if listing.find('a', class_='card__media') else "Link Not Available"
        link_tag = listing.find('a', class_='card__media')
        if link_tag and 'href' in link_tag.attrs:
            link = link_tag['href']
            # Check if the link is partial and complete it if necessary
            if link.startswith('//'):
                link = 'https:' + link
            elif link.startswith('/'):
                link = 'https://www.royallepage.ca' + link
        else:
            link = "Link Not Available"

        # Print or store extracted data
        print(f"Listing ID: {listing_id}")
        print(f"HouseType: {housetype}")
        print(f"Type: {type_}")
        print(f"Price: {price}")
        print(f"Address1: {address1}")
        print(f"Address2: {address2}")
        print(f"Link: {link}")
        print(f"linkTag:{link_tag}")
        print('-' * 50)

        # Append to data list
        '''data.append({
            "Listing ID": listing_id,
            "HouseType": housetype,
            "Type": type_,
            "Price": price,
            "Address1": address1,
            "Address2": address2,
            "Link": link
        })'''

    except AttributeError:
        continue

# Save data to CSV
'''df = pd.DataFrame(data)
df.to_csv('royal_lepage_listings.csv', index=False)
print("Data successfully saved to royal_lepage_listings.csv")'''
