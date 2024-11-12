import pandas as pd
from pymongo import MongoClient
from sklearn.preprocessing import OneHotEncoder

# Connect to MongoDB
client = MongoClient('mongodb+srv://ernestyawgaisie:ernestyawgaisie@cluster0.dvjsafm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['real_estate']
collection = db['raw_data_with_price_cleaned']

# Retrieve data from MongoDB
data = pd.DataFrame(list(collection.find()))

# Additional Cleaning
# Convert 'Size (sqft)' to numeric, handling errors as NaN
data['Size (sqft)'] = pd.to_numeric(data['Size (sqft)'].str.replace(',', ''), errors='coerce')

# Convert Bedrooms and Bathrooms to numeric, handling non-numeric as NaN
data['Bedrooms'] = pd.to_numeric(data['Bedrooms'], errors='coerce')
data['Bathrooms'] = pd.to_numeric(data['Bathrooms'], errors='coerce')

# Drop rows with missing values in critical columns
data.dropna(subset=['Price', 'Bedrooms', 'Bathrooms', 'Size (sqft)', 'Location'], inplace=True)

# Encode 'Location' using One-Hot Encoding
location_encoded = pd.get_dummies(data['Location'], prefix='Location')

# Combine the encoded location columns with the original DataFrame
data = pd.concat([data, location_encoded], axis=1)

# Drop the original 'Location' column as it's now encoded
data.drop(columns=['Location'], inplace=True)

# Select features (X) and target (y)
X = data[['Bedrooms', 'Bathrooms', 'Size (sqft)'] + list(location_encoded.columns)]
y = data['Price']

# Display a sample of the cleaned and prepared data
print("Sample data ready for training:")
print(data.head())
