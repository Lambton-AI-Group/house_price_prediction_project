import pandas as pd
import pymongo
from pymongo import MongoClient
import re
import os

# MongoDB Atlas Connection String (Replace with your own)
uri = "mongodb+srv://ridhampatel2041:Mpz7Hm5i2WfsHaOG@cluster0.vsseydq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client['real_estate_db']
collection = db['properties']

# Fetch data from MongoDB
data = list(collection.find())
df = pd.DataFrame(data)

# Function to clean the price field
def clean_price(price_str):
    # Remove '$', 'From' prefixes, and commas, then convert to numeric value
    price_str = re.sub(r'[^\d.]', '', str(price_str))
    try:
        return float(price_str)
    except ValueError:
        return None

# Clean 'price' column by removing unwanted characters
df['price'] = df['price'].apply(clean_price)

# Convert 'bed' and 'bath' to integers, and clean 'size-sqft' if applicable
df['bed'] = pd.to_numeric(df['bed'], errors='coerce').fillna(0).astype(int)
df['bath'] = pd.to_numeric(df['bath'].replace('+', ''), errors='coerce').fillna(0).astype(int)
df['size-sqft'] = df['size-sqft'].apply(lambda x: int(x.replace(',', '').strip()) if isinstance(x, str) else x)
