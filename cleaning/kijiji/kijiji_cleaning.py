import pandas as pd
from pymongo import MongoClient

# Load the scraped data from CSV
data = pd.read_csv('/Users/ernestgaisie/Desktop/Housing Prices Project/scrape/kijiji/ontario/ontario_listings.csv')

# Data Cleaning

# 1. Clean 'Price': Remove '$' and ',' then convert to float
data['Price'] = data['Price'].replace('[\$,]', '', regex=True).astype(float)

# 2. Convert 'Size (sqft)' to numeric, handling non-numeric values as NaN
data['Size (sqft)'] = pd.to_numeric(data['Size (sqft)'].str.replace(',', ''), errors='coerce')

# 3. Handle missing values in 'Size (sqft)' by filling with the median value
data['Size (sqft)'].fillna(data['Size (sqft)'].median(), inplace=True)

# 4. Convert 'Bedrooms' and 'Bathrooms' to numeric, handling non-numeric values as NaN
data['Bedrooms'] = pd.to_numeric(data['Bedrooms'], errors='coerce')
data['Bathrooms'] = pd.to_numeric(data['Bathrooms'], errors='coerce')

# 5. Drop rows with critical missing values in columns like 'Price', 'Bedrooms', or 'Bathrooms'
data.dropna(subset=['Price', 'Bedrooms', 'Bathrooms'], inplace=True)

# Display cleaned data to verify
print("Cleaned Data Sample:")
print(data.head())

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['real_estate']
collection = db['cleaned_data']

# Convert DataFrame to dictionary format for MongoDB insertion
data_dict = data.to_dict("records")

# Insert cleaned data into MongoDB
collection.insert_many(data_dict)
print("Data has been successfully stored in MongoDB.")
