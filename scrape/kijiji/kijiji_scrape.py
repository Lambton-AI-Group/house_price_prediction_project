import requests
from bs4 import BeautifulSoup

# Kijiji URL for condos for sale in Canada
url = 'https://www.kijiji.ca/b-house-for-sale/ontario/c35l9004?sort=dateDesc'

# Headers to mimic a browser request (important to avoid being blocked)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

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
            print("Error: Listing ID not found")
            listing_id = None

        # Title
        try:
            title = listing.find(
                'a', {'data-testid': 'listing-link'}).text.strip()
        except AttributeError:
            print(f"Error: Title not found for listing {listing_id}")
            title = None

        # Price
        try:
            price = listing.find(
                'p', {'data-testid': 'listing-price'}).text.strip()
        except AttributeError:
            print(f"Error: Price not found for listing {listing_id}")
            price = None

        # Location
        try:
            location = listing.find(
                'p', {'data-testid': 'listing-location'}).text.strip()
        except AttributeError:
            print(f"Error: Location not found for listing {listing_id}")
            location = None

        # Link
        try:
            link = listing.find('a', {'data-testid': 'listing-link'})['href']
            full_link = f"{link}"
        except AttributeError:
            print(f"Error: Link not found for listing {listing_id}")
            full_link = None

        # Description
        try:
            description = listing.find(
                'p', {'data-testid': 'listing-description'}).text.strip()
        except AttributeError:
            print(f"Error: Description not found for listing {listing_id}")
            description = None

        # Fetching details from the detailed page
        try:
            detail_response = requests.get(full_link, headers=headers)
            detail_soup = BeautifulSoup(detail_response.content, 'html.parser')

            # Bedrooms
            try:
                bedrooms = detail_soup.find('dd', {'itemprop': 'numberOfBedrooms'}).text.strip()
            except AttributeError:
                bedrooms = 'N/A'
                print(f"Error: Bedrooms not found for listing {listing_id}")

            # Bathrooms
            try:
                bathrooms = detail_soup.find('dd', {'itemprop': 'numberOfBathroomsTotal'}).text.strip()
            except AttributeError:
                bathrooms = 'N/A'
                print(f"Error: Bathrooms not found for listing {listing_id}")

            # Size (sqft)
            try:
                size = detail_soup.find('dd', {'itemprop': 'floorSize'}).text.strip()
            except AttributeError:
                size = 'N/A'
                print(f"Error: Size not found for listing {listing_id}")

        except Exception as e:
            print(f"Error fetching details page for listing {listing_id}: {str(e)}")

        # Output the extracted data
        print(f"Listing ID: {listing_id}")
        print(f"Title: {title}")
        print(f"Price: {price}")
        print(f"Location: {location}")
        print(f"Link: {full_link}")
        print(f"Description: {description}")
        print(f"Bedrooms: {bedrooms}")
        print(f"Bathrooms: {bathrooms}")
        print(f"Size (sqft): {size}")
        print('-' * 50)

    except Exception as e:
        # General exception for debugging other issues
        print(f"An unexpected error occurred for listing {listing_id}: {str(e)}")
