import pandas as pd
from pymongo import MongoClient

# Load the scraped data from CSV
data = pd.read_csv(
    '/Users/ernestgaisie/Desktop/Housing Prices Project/scrape/kijiji/ontario/ontario_listings.csv')

# Clean the Price column: Remove '$' and ',' then convert to numeric, handling non-numeric entries as NaN
data['Price'] = data['Price'].replace('[\$,]', '', regex=True)  # Remove symbols
data['Price'] = pd.to_numeric(data['Price'], errors='coerce')  # Convert to float, setting non-numeric as NaN

# Drop rows where Price is NaN
data.dropna(subset=['Price'], inplace=True)

# Connect to MongoDB
client = MongoClient('mongodb+srv://ernestyawgaisie:ernestyawgaisie@cluster0.dvjsafm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['real_estate']  # Use database named 'real_estate'
collection = db['raw_data_with_price_cleaned']  # Collection for price-cleaned data

# Convert DataFrame to dictionary format for MongoDB insertion
data_dict = data.to_dict("records")

# Insert cleaned data into MongoDB
collection.insert_many(data_dict)
print("Data with cleaned 'Price' has been successfully stored in MongoDB.")