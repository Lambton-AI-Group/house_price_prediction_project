import requests
from bs4 import BeautifulSoup
import csv
import time
import os

# Base URL for Kijiji listings
base_url = 'https://www.kijiji.ca/b-house-for-sale/ontario/c35l9004?sort=dateDesc'

# Headers to mimic a browser request (important to avoid being blocked)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Function to scrape data from a page


def scrape_listings(page_num):
    # Update the URL for the current page
    url = f"{base_url}&page={page_num}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Finding the listings on the page
    listings = soup.find_all('li', {
                             'data-testid': lambda value: value and value.startswith('listing-card-list-item')})

    data = []

    for listing in listings:
        try:
            # Listing ID
            try:
                listing_id = listing.find(
                    'section', {'data-testid': 'listing-card'})['data-listingid']
            except AttributeError:
                listing_id = 'N/A'
                print("Error: Listing ID not found")

            # Title
            try:
                title = listing.find(
                    'a', {'data-testid': 'listing-link'}).text.strip()
            except AttributeError:
                title = 'N/A'
                print(f"Error: Title not found for listing {listing_id}")

            # Price
            try:
                price = listing.find(
                    'p', {'data-testid': 'listing-price'}).text.strip()
            except AttributeError:
                price = 'N/A'
                print(f"Error: Price not found for listing {listing_id}")

            # Location
            try:
                location = listing.find(
                    'p', {'data-testid': 'listing-location'}).text.strip()
            except AttributeError:
                location = 'N/A'
                print(f"Error: Location not found for listing {listing_id}")

            # Link
            try:
                link = listing.find(
                    'a', {'data-testid': 'listing-link'})['href']
                full_link = f"{link}"
            except AttributeError:
                full_link = 'N/A'
                print(f"Error: Link not found for listing {listing_id}")

            # Description
            try:
                description = listing.find(
                    'p', {'data-testid': 'listing-description'}).text.strip()
            except AttributeError:
                description = 'N/A'
                print(f"Error: Description not found for listing {listing_id}")

            # Fetching details from the detailed page
            try:
                detail_response = requests.get(full_link, headers=headers)
                detail_soup = BeautifulSoup(
                    detail_response.content, 'html.parser')

                # Bedrooms
                try:
                    bedrooms = detail_soup.find(
                        'dd', {'itemprop': 'numberOfBedrooms'}).text.strip()
                except AttributeError:
                    bedrooms = 'N/A'
                    print(
                        f"Error: Bedrooms not found for listing {listing_id}")

                # Bathrooms
                try:
                    bathrooms = detail_soup.find(
                        'dd', {'itemprop': 'numberOfBathroomsTotal'}).text.strip()
                except AttributeError:
                    bathrooms = 'N/A'
                    print(
                        f"Error: Bathrooms not found for listing {listing_id}")

                # Size (sqft)
                try:
                    size = detail_soup.find(
                        'dd', {'itemprop': 'floorSize'}).text.strip()
                except AttributeError:
                    size = 'N/A'
                    print(f"Error: Size not found for listing {listing_id}")

                # Time Posted (Date)
                try:
                    time_posted = detail_soup.find(
                        'div', {'itemprop': 'datePosted'})['content']
                except AttributeError:
                    time_posted = 'N/A'
                    print(
                        f"Error: Time posted not found for listing {listing_id}")

            except Exception as e:
                print(
                    f"Error fetching details page for listing {listing_id}: {str(e)}")
                bedrooms, bathrooms, size, time_posted = 'N/A', 'N/A', 'N/A', 'N/A'

            # Collect the data
            data.append([listing_id, title, price, location, full_link,
                        description, time_posted, bedrooms, bathrooms, size])

        except Exception as e:
            print(
                f"An unexpected error occurred for listing {listing_id}: {str(e)}")

    return data


csv_file_name = 'ontario_listings.csv'
# Determine if the file already exists to decide the write mode
file_exists = os.path.isfile(csv_file_name)

# Open CSV file to save the data
with open(csv_file_name, 'a' if file_exists else 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    # Write header only if file doesn't exist
    if not file_exists:
        writer.writerow(['Listing ID', 'Title', 'Price', 'Location', 'Link',
                        'Description', 'Time Posted', 'Bedrooms', 'Bathrooms', 'Size (sqft)'])

    # Scraping the first 1211 pages (adjust as needed)
    for page_num in range(933, 1211):
        print(f"Scraping page {page_num}...")
        listings_data = scrape_listings(page_num)

        # Write data for the current page to CSV
        for row in listings_data:
            writer.writerow(row)

        # Optional: pause to prevent overwhelming the server
        time.sleep(2)

print("Scraping completed. Data saved to kijiji_listings.csv")
