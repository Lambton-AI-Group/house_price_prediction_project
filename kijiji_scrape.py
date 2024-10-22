import requests
from bs4 import BeautifulSoup

# Kijiji URL for condos for sale in Canada
url = 'https://www.kijiji.ca/b-condo-for-sale/mississauga-peel-region/1+bedroom/c643l1700276a139?sort=dateDesc'

# Headers to mimic a browser request (important to avoid being blocked)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Sending a request to fetch the HTML content
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# Finding the listings on the page
listings = soup.find_all('li', {'data-testid': lambda value: value and value.startswith('listing-card-list-item')})

# Looping through listings and extract data
for listing in listings:
    try:
        # Listing ID
        listing_id = listing.find('section', {'data-testid': 'listing-card'})['data-listingid']
        
        # Title
        title = listing.find('a', {'data-testid': 'listing-link'}).text.strip()
        
        # Price
        price = listing.find('p', {'data-testid': 'listing-price'}).text.strip()
        
        # Location
        location = listing.find('p', {'data-testid': 'listing-location'}).text.strip()
        
        # Link
        link = listing.find('a', {'data-testid': 'listing-link'})['href']
        full_link = f"https://www.kijiji.ca{link}"
        
        # Description
        description = listing.find('p', {'data-testid': 'listing-description'}).text.strip()

        # Output the extracted data
        print(f"Listing ID: {listing_id}")
        print(f"Title: {title}")
        print(f"Price: {price}")
        print(f"Location: {location}")
        print(f"Link: {full_link}")
        print(f"Description: {description}")
        print('-' * 50)

    except AttributeError:
        # Handle any missing data gracefully
        continue
