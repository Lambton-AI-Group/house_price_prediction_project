import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Kijiji URL for houses for sale in Ontario, sorted by date
url = 'https://www.kijiji.ca/b-house-for-sale/ontario/c35l9004?sort=dateDesc'

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# List to store the data
data = []

# Sending a request to fetch the HTML content
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# Finding the listings on the page
listings = soup.find_all('li', {
                         'data-testid': lambda value: value and value.startswith('listing-card-list-item')})

# Looping through listings and extract data
for listing in listings:
    try:
        # Listing ID
        try:
            listing_id = listing.find(
                'section', {'data-testid': 'listing-card'})['data-listingid']
        except AttributeError:
            listing_id = None

        # Title
        try:
            title = listing.find(
                'a', {'data-testid': 'listing-link'}).text.strip()
        except AttributeError:
            title = None

        # Price
        try:
            price = listing.find(
                'p', {'data-testid': 'listing-price'}).text.strip()
        except AttributeError:
            price = None

        # Location
        try:
            location = listing.find(
                'p', {'data-testid': 'listing-location'}).text.strip()
        except AttributeError:
            location = None

        # Link
        try:
            link = listing.find('a', {'data-testid': 'listing-link'})['href']
            full_link = f"{link}"
        except AttributeError:
            full_link = None

        # Description
        try:
            description = listing.find(
                'p', {'data-testid': 'listing-description'}).text.strip()
        except AttributeError:
            description = None

        # Fetching additional details from the detailed page
        bedrooms = bathrooms = size = 'N/A'  # Set default values
        if full_link:
            try:
                detail_response = requests.get(full_link, headers=headers)
                detail_soup = BeautifulSoup(
                    detail_response.content, 'html.parser')

                # Bedrooms
                try:
                    bedrooms = detail_soup.find(
                        'dd', {'itemprop': 'numberOfBedrooms'}).text.strip()
                except AttributeError:
                    print(
                        f"Error: Bedrooms not found for listing {listing_id}")

                # Bathrooms
                try:
                    bathrooms = detail_soup.find(
                        'dd', {'itemprop': 'numberOfBathroomsTotal'}).text.strip()
                except AttributeError:
                    print(
                        f"Error: Bathrooms not found for listing {listing_id}")

                # Size (sqft)
                try:
                    size = detail_soup.find(
                        'dd', {'itemprop': 'floorSize'}).text.strip()
                except AttributeError:
                    print(f"Error: Size not found for listing {listing_id}")

            except Exception as e:
                print(
                    f"Error fetching details page for listing {listing_id}: {str(e)}")

        # Append the extracted data to the list
        data.append({
            'Listing ID': listing_id,
            'Title': title,
            'Price': price,
            'Location': location,
            'Link': full_link,
            'Description': description,
            'Bedrooms': bedrooms,
            'Bathrooms': bathrooms,
            'Size (sqft)': size
        })

        # Adding a small delay to avoid being blocked
        time.sleep(1)

    except Exception as e:
        print(f"An error occurred for listing {listing_id}: {str(e)}")

# Convert data to DataFrame and save as CSV
df = pd.DataFrame(data)
df.to_csv('automation/scrape/data/kijiji_listings.csv', index=False)
print("Data scraped and saved to scrape/data/kijiji_listings.csv")
