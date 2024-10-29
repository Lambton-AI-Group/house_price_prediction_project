import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd

# Headers to simulate a browser request
head = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.realtor.com/",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

# Base URL pattern for pagination
base_url = "https://www.realtor.com/realestateandhomes-search/Ontario_CA/pg-{}"

# List to store all house listings
all_listings = []

# Start pagination from page 1
page = 1
max_retries = 5
retries = 0

while retries < max_retries:
    target_url = base_url.format(page)
    resp = requests.get(target_url, headers=head)
    print(f"Fetching page {page}, status code: {resp.status_code}")

    if resp.status_code == 404:
        print(f"Page {page} returned 404. Checking for additional retries.")
        retries += 1
        page += 1
        continue
    elif resp.status_code != 200:
        print("Failed to retrieve data. Stopping.")
        break

    soup = BeautifulSoup(resp.text, 'html.parser')
    allData = soup.find_all("div", {"class": "BasePropertyCard_propertyCardWrap__30VCU"})

    # If no more listings are found on the page, stop pagination
    if not allData:
        print(f"No more data found on page {page}. Stopping.")
        break

    # Reset retries if we get a valid page
    retries = 0

    # Extract data from each listing
    for data in allData:
        o = {}

        try:
            o["price"] = data.find("div", {"data-testid": "card-price"}).text
        except:
            o["price"] = None

        try:
            metaData = data.find("ul", {"class": "PropertyMetastyles__StyledPropertyMeta-rui__sc-1g5rdjn-0 KKDDp card-meta"})
            if metaData:
                o["bed"] = metaData.find("li", {"data-testid": "property-meta-beds"}).find("span", {"data-testid": "meta-value"}).text
                o["bath"] = metaData.find("li", {"data-testid": "property-meta-baths"}).find("span", {"data-testid": "meta-value"}).text
                o["size-sqft"] = metaData.find("li", {"data-testid": "property-meta-sqft"}).find("span", {"data-testid": "meta-value"}).text
        except:
            o["bed"] = o["bath"] = o["size-sqft"] = None

        try:
            address1 = data.find("div", {"data-testid": "card-address-1"}).text
            address2 = data.find("div", {"data-testid": "card-address-2"}).text
            o["address"] = f"{address1}, {address2}"
        except:
            o["address"] = None

        if o["price"] and o["address"] and o["bed"] and o["bath"] and o["size-sqft"]:
            all_listings.append(o)

    # Increment page number for next loop iteration
    page += 1

    # Optional: Sleep for a random short interval to avoid getting blocked
    time.sleep(random.uniform(1, 3))

# Save to CSV using pandas
df = pd.DataFrame(all_listings)
df.to_csv('real_estate_listings_extended.csv', index=False)

print(f"Total listings extracted: {len(all_listings)} and saved to 'real_estate_listings_extended.csv'")
