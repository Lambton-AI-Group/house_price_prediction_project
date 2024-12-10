from flask import Flask, request, jsonify
import joblib
import pandas as pd
from pymongo import MongoClient
import shap
import numpy as np
from twilio.rest import Client
import os
import requests



# Load the model, encoders, and scaler
loaded_model = joblib.load('automation/api/xgboost_model.pkl')
le_type = joblib.load('automation/api/type_encoder.pkl')
le_province_city = joblib.load('automation/api/province_city_encoder.pkl')
scaler = joblib.load('automation/api/scaler.pkl')

# Connect to MongoDB
client = MongoClient(
    'mongodb+srv://ernestyawgaisie:ernestyawgaisie@cluster0.dvjsafm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['real_estate']
collection = db['raw_data_with_price_cleaned']

# Initialize Flask app
app = Flask(__name__)

# SHAP Explainer
explainer = shap.TreeExplainer(loaded_model)

# Endpoint 1: Predict Price for a Specific Property


@app.route('/predict-price', methods=['POST'])
def predict_price():
    data = request.get_json()
    bedrooms = data.get('Bedrooms')
    bathrooms = data.get('Bathrooms')
    province_city = data.get('Province_City')
    property_type = data.get('Type')

    # Encode province_city and property_type
    encoded_province_city = le_province_city.transform([province_city])[0]
    encoded_type = le_type.transform([property_type])[0]

    # Prepare input data
    input_data = {
        'Bedrooms': bedrooms,
        'Bathrooms': bathrooms,
        'Province_City': encoded_province_city,
        'Type': encoded_type
    }

    # Standardize numerical features
    numerical_data = pd.DataFrame([{
        'Bedrooms': bedrooms,
        'Bathrooms': bathrooms
    }])
    numerical_data[['Bedrooms', 'Bathrooms']
                   ] = scaler.transform(numerical_data)

    # Combine standardized numerical features with encoded categorical features
    input_df = pd.DataFrame([[
        numerical_data['Bedrooms'][0],
        numerical_data['Bathrooms'][0],
        encoded_province_city,
        encoded_type
    ]], columns=['Bedrooms', 'Bathrooms', 'Province_City', 'Type'])

    # Predict
    predicted_price = loaded_model.predict(input_df)[0]

    return jsonify({
        "predicted_price": f"${predicted_price:,.2f}"
    })

# Endpoint 2: Get Listings Below Predicted Price with SHAP Insights
def format_shap_contributions(contributions):
    """Convert SHAP values into a structured dictionary."""
    insights = {"positive": [], "negative": []}

    for feature, value in contributions.items():
        impact = round(value, 2)
        entry = {
            "feature": feature.replace('_', ' '),
            "influence": "positive" if impact > 0 else "negative",
            "value": abs(impact),
            "text": f"{feature.replace('_', ' ').capitalize()} "
                    f"{'increased' if impact > 0 else 'reduced'} the estimated price by ${abs(impact):,.2f}."
        }

        if impact > 0:
            insights["positive"].append(entry)
        elif impact < 0:
            insights["negative"].append(entry)

    if not insights["positive"] and not insights["negative"]:
        insights["neutral"] = [{"text": "No significant features affected the prediction."}]

    return insights


@app.route('/listings-below-prediction', methods=['POST'])
def listings_below_prediction():
    try:
        # Extract data from request
        data = request.get_json(force=True)
        bedrooms = data.get('Bedrooms', 0)
        bathrooms = data.get('Bathrooms', 0)
        province_city = data.get('Province_City', 'Ontario_Toronto').strip()
        property_type = data.get('Type', 'House').strip()
        limit = data.get('limit', 10)

        # Default feature values
        median_family_income = data.get('Median_Family_Income', 75000)
        population = data.get('Population', 10000)

        # Encode categorical features
        try:
            encoded_province_city = le_province_city.transform([province_city])[0]
            encoded_type = le_type.transform([property_type])[0]
        except ValueError as e:
            return jsonify({
                "error": f"Invalid location or property type provided: {str(e)}"
            }), 400

        # Standardize numerical features
        numerical_data = np.array([[bedrooms, bathrooms, population, median_family_income]])
        scaled_data = scaler.transform(numerical_data)[0]

        # Combine numerical and categorical features
        prediction_input = np.array([np.concatenate((scaled_data, [encoded_province_city, encoded_type]))])

        # Predict price
        predicted_price = float(loaded_model.predict(prediction_input)[0])

        # Query MongoDB for cheaper listings
        raw_listings = collection.find({
            'Price': {'$lt': predicted_price},
            '$expr': {
                '$and': [
                    {'$lte': [{'$convert': {'input': '$Bedrooms', 'to': 'int', 'onError': 0}}, bedrooms]},
                    {'$lte': [{'$convert': {'input': '$Bathrooms', 'to': 'int', 'onError': 0}}, bathrooms]}
                ]
            }
        }).limit(limit)

        # Filter unique listings by Listing ID
        unique_listings = {}
        for listing in raw_listings:
            listing_id = listing.get('Listing ID')
            if listing_id not in unique_listings:
                listing['_id'] = str(listing['_id'])  # Convert ObjectId to string
                unique_listings[listing_id] = listing

        listings = list(unique_listings.values())

        # Extract SHAP insights
        for listing in listings:
            try:
                # Use default values if missing
                listing_province_city = listing.get('Province_City', 'Ontario_Toronto')
                listing_property_type = listing.get('Type', 'House')

                # Prepare listing data
                listing_data = pd.DataFrame([{
                    'Bedrooms': int(listing.get('Bedrooms', 0)),
                    'Bathrooms': int(listing.get('Bathrooms', 0)),
                    'Population': population,
                    'Median_Family_Income': median_family_income,
                    'Province_City': listing_province_city,
                    'Type': listing_property_type
                }])

                # Encode categorical features
                listing_data['Province_City'] = le_province_city.transform(listing_data['Province_City'])
                listing_data['Type'] = le_type.transform(listing_data['Type'])

                # Standardize numerical features
                listing_data[['Bedrooms', 'Bathrooms', 'Population', 'Median_Family_Income']] = scaler.transform(
                    listing_data[['Bedrooms', 'Bathrooms', 'Population', 'Median_Family_Income']]
                )

                # Calculate SHAP values
                shap_values = explainer.shap_values(listing_data)

                # Format and attach SHAP contributions
                feature_contributions = dict(zip(
                    ['Bedrooms', 'Bathrooms', 'Population', 'Median_Family_Income', 'Province_City', 'Type'],
                    map(float, shap_values[0])  # Convert to float
                ))

                # Attach structured insights
                listing['SHAP_Contributions'] = format_shap_contributions(feature_contributions)

            except Exception as e:
                print(f"SHAP Error for listing {listing['Title']}: {str(e)}")
                listing['SHAP_Contributions'] = {
                    "error": f"SHAP calculation failed: {str(e)}"
                }

        # Return the updated response
        return jsonify({
            'predicted_price': f"${predicted_price:,.2f}",
            'listings_below_prediction': listings
        })

    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500

# Endpoint 3: Suggest Cheaper Locations


@app.route('/suggest-cheaper-locations', methods=['POST'])
def suggest_cheaper_locations():
    try:
        # Extract input data from request
        data = request.get_json()
        bedrooms = data.get('Bedrooms', 0)
        bathrooms = data.get('Bathrooms', 0)
        province_city = data.get('Province_City', 'Ontario_Toronto').strip()
        property_type = data.get('Type', 'House').strip()

        # Default feature values
        median_family_income = data.get('Median_Family_Income', 75000)
        population = data.get('Population', 10000)

        # Encode features for prediction
        try:
            encoded_province_city = le_province_city.transform([province_city])[0]
            encoded_type = le_type.transform([property_type])[0]
        except ValueError as e:
            return jsonify({
                "error": f"Invalid property type or location provided: {str(e)}"
            }), 400

        # Prepare input data for prediction
        numerical_data = np.array([[bedrooms, bathrooms, population, median_family_income]])
        scaled_data = scaler.transform(numerical_data)[0]

        # Combine numerical and categorical features
        input_df = np.array([np.concatenate((scaled_data, [encoded_province_city, encoded_type]))])

        # Predict the price
        predicted_price = float(loaded_model.predict(input_df)[0])

        # Query MongoDB using only 'Location' without 'Province_City'
        cheaper_locations = collection.distinct(
            'Location', {
                'Price': {'$lt': predicted_price},
            }
        )

        # Format the response
        suggestions = [location for location in cheaper_locations if location is not None]

        return jsonify({
            'predicted_price': f"${predicted_price:,.2f}",
            'cheaper_locations': suggestions
        })

    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = "+17692475485"

# MongoDB connection
db = client['real_estate']
users_collection = db['users']


# Twilio API URL
TWILIO_API_URL = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"


@app.route('/send-sms', methods=['POST'])
def send_sms():
    try:
        # Fetch all users with phone numbers
        users = users_collection.find({"Phone Number": {"$exists": True, "$ne": None}})
        notifications = []

        # Send SMS notifications
        for user in users:
            phone_number = user.get("Phone Number")

            # Prepare the payload
            payload = {
                'To': phone_number,
                'From': TWILIO_PHONE_NUMBER,
                'Body': "You have new listings matching your preferences. Kindly check them out here."
            }

            # Hit the Twilio API
            response = requests.post(
                TWILIO_API_URL,
                data=payload,
                auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            )

            # Check response status
            if response.status_code == 201:
                message_sid = response.json().get('sid')
                notifications.append({
                    "phone_number": phone_number,
                    "message_sid": message_sid,
                    "status": "sent"
                })
                print(f"Notification sent to {phone_number}: {message_sid}")
            else:
                notifications.append({
                    "phone_number": phone_number,
                    "status": "failed",
                    "error": response.json()
                })
                print(f"Failed to send SMS to {phone_number}: {response.text}")

        return jsonify({
            "status": "success",
            "notifications": notifications
        }), 200

    except Exception as e:
        return jsonify({
            "status": "failed",
            "error": str(e)
        }), 500
    

if __name__ == '__main__':
    app.run(debug=True, port=5005)

