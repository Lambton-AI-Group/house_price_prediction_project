import pandas as pd
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import LabelEncoder
import joblib
import numpy as np


def load_data_from_mongo():
    # Connect to MongoDB and retrieve the data
    client = MongoClient(
        'mongodb+srv://ernestyawgaisie:ernestyawgaisie@cluster0.dvjsafm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    db = client['real_estate']
    collection = db['raw_data_with_price_cleaned']
    data = pd.DataFrame(list(collection.find()))
    return data


def preprocess_data(data):
    # Remove duplicates
    data = data.drop_duplicates(subset=data.columns.difference(['_id']))

    # Convert Bedrooms and Bathrooms to numeric
    data['Bedrooms'] = pd.to_numeric(data['Bedrooms'], errors='coerce')
    data['Bathrooms'] = pd.to_numeric(data['Bathrooms'], errors='coerce')

    # Drop rows with missing values in essential columns
    data.dropna(subset=['Price', 'Bedrooms',
                'Bathrooms', 'Location'], inplace=True)

    # Label Encode the 'Location' column
    label_encoder = LabelEncoder()
    data['Location'] = label_encoder.fit_transform(data['Location'])

    # Save label encoder for use in predictions
    joblib.dump(label_encoder,
                'automation/model_training/location_label_encoder.pkl')

    # Define features and target
    X = data[['Bedrooms', 'Bathrooms', 'Location']]
    y = data['Price']
    return X, y


def train_model(X, y):
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    # Initialize and train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Evaluate the model
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    print("Model Evaluation:")
    print(f"Mean Absolute Error (MAE): {mae}")
    print(f"Root Mean Squared Error (RMSE): {rmse}")

    # Save trained model and columns
    joblib.dump(model, 'automation/model_training/house_price_model.pkl')
    joblib.dump(X.columns, 'automation/model_training/trained_columns.pkl')
    print("Model and label encoder saved.")
    return model


def main():
    # Step 1: Load data
    data = load_data_from_mongo()

    # Step 2: Preprocess data
    X, y = preprocess_data(data)

    # Step 3: Train and evaluate model
    train_model(X, y)


if __name__ == "__main__":
    main()
