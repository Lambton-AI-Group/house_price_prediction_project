from flask import Flask, request, jsonify
import joblib
import pandas as pd
from pymongo import MongoClient

# Load the model and label encoder
model = joblib.load('automation/model_training/house_price_model.pkl')
label_encoder = joblib.load('automation/model_training/location_label_encoder.pkl')
trained_columns = joblib.load('automation/model_training/trained_columns.pkl')

# Connect to MongoDB
client = MongoClient(
    'mongodb+srv://ernestyawgaisie:ernestyawgaisie@cluster0.dvjsafm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['real_estate']
collection = db['raw_data_with_price_cleaned']

app = Flask(__name__)

# Endpoint 1: Predict Price for a Specific Property


@app.route('/predict-price', methods=['POST'])
def predict_price():
    data = request.get_json()
    bedrooms = data.get('Bedrooms')
    bathrooms = data.get('Bathrooms')
    location_name = data.get('Location')

    # Encode location
    encoded_location = label_encoder.transform([location_name])[0]

    # Prepare input data
    input_data = {'Bedrooms': bedrooms,
                  'Bathrooms': bathrooms, 'Location': encoded_location}
    input_df = pd.DataFrame([input_data], columns=trained_columns).fillna(0)

    # Predict
    predicted_price = model.predict(input_df)[0]

    return jsonify({
        "predicted_price": f"${predicted_price:,.2f}"
    })

# Endpoint 2: Get Listings Below Predicted Price


@app.route('/listings-below-prediction', methods=['POST'])
def listings_below_prediction():
    data = request.get_json(force=True)
    bedrooms = data.get('Bedrooms', 0)
    bathrooms = data.get('Bathrooms', 0)
    location_name = data.get('Location', '')
    limit = data.get('limit', 10)  # Default limit of 10

    # Encode location using label encoder
    encoded_location = label_encoder.transform([location_name])[0]

    # Create a DataFrame for prediction
    input_data = {'Bedrooms': bedrooms,
                  'Bathrooms': bathrooms, 'Location': encoded_location}
    input_df = pd.DataFrame([input_data], columns=trained_columns).fillna(0)

    # Get the predicted price from the model as a numeric value
    predicted_price = float(model.predict(input_df)[0])

    # Query MongoDB for listings with actual prices below the predicted price and bedrooms/bathrooms <= specified values
    listings = list(collection.find({
        'Price': {'$lt': predicted_price},
        '$expr': {
            '$and': [
                {'$lte': [{'$convert': {'input': '$Bedrooms',
                                        'to': 'int', 'onError': 0}}, bedrooms]},
                {'$lte': [{'$convert': {'input': '$Bathrooms',
                                        'to': 'int', 'onError': 0}}, bathrooms]}
            ]
        }
    }).limit(limit))

    # Filter for unique listings by Listing ID
    unique_listings = {}
    for listing in listings:
        listing_id = listing.get('Listing ID')
        if listing_id not in unique_listings:
            unique_listings[listing_id] = {
                'Listing ID': listing_id,
                'Title': listing.get('Title'),
                'Actual Price': listing.get('Price'),
                'Predicted Price': f"${predicted_price:,.2f}",
                'Location': listing.get('Location'),
                'Link': listing.get('Link')
            }

    # Convert unique listings to a list
    listings_below = list(unique_listings.values())

    # Return listings with predicted price included in the response
    return jsonify({
        'predicted_price': f"${predicted_price:,.2f}",
        'listings_below_prediction': listings_below
    })


if __name__ == '__main__':
    app.run(debug=True, port=5005)
