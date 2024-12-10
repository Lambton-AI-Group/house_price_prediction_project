from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb+srv://ernestyawgaisie:ernestyawgaisie@cluster0.dvjsafm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['real_estate']
users_collection = db['users']

# Define user schema
users = [
    {
        "Name": "Ernest Gaisie",
        "Phone Number": "+16476463469",
        "Type": "House",
        "Bedrooms": 3,
        "Bathrooms": 2,
        "Location": "Toronto"
    },
    {
        "Name": "Jane Smith",
        "Phone Number": "+1-555-5678",
        "Type": "Condo",
        "Bedrooms": 2,
        "Bathrooms": 1,
        "Location": "Vancouver"
    },
    {
        "Name": "Emily Johnson",
        "Phone Number": "+1-555-9101",
        "Type": "Apartment",
        "Bedrooms": 1,
        "Bathrooms": 1,
        "Location": "Montreal"
    }
]

# Insert users into the collection
result = users_collection.insert_many(users)

# Verify insertion
inserted_ids = result.inserted_ids
inserted_ids
