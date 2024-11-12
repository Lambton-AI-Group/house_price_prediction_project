import pandas as pd
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import LabelEncoder
import numpy as np
import matplotlib.pyplot as plt
import joblib

# Step 1: Connect to MongoDB and Load Data
client = MongoClient(
    'mongodb+srv://ernestyawgaisie:ernestyawgaisie@cluster0.dvjsafm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['real_estate']
collection = db['raw_data_with_price_cleaned']

# Retrieve data from MongoDB
data = pd.DataFrame(list(collection.find()))

# Step 2: Handle Duplicates
# Identify and remove duplicate rows, excluding the '_id' column
duplicate_rows = data.duplicated(subset=data.columns.difference(['_id']))
print(f"Number of duplicate rows: {duplicate_rows.sum()}")
data = data.drop_duplicates(subset=data.columns.difference(['_id']))
print(f"Data shape after removing duplicates: {data.shape}")

# Step 3: Data Cleaning and Preprocessing
# Convert Bedrooms and Bathrooms to numeric, handling non-numeric as NaN
data['Bedrooms'] = pd.to_numeric(data['Bedrooms'], errors='coerce')
data['Bathrooms'] = pd.to_numeric(data['Bathrooms'], errors='coerce')

# Drop rows with missing values in essential columns
data.dropna(subset=['Price', 'Bedrooms',
            'Bathrooms', 'Location'], inplace=True)

# Label Encode the 'Location' column
label_encoder = LabelEncoder()
data['Location'] = label_encoder.fit_transform(data['Location'])

# Step 4: Prepare Features (X) and Target (y)
# Ensure 'Price' is excluded from X, as it is the target variable
X = data.drop(columns=['_id', 'Listing ID', 'Title', 'Link',
              'Description', 'Time Posted', 'Size (sqft)', 'Price'])
y = data['Price']

# Step 5: Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# Step 6: Model Training
model = LinearRegression()
model.fit(X_train, y_train)

# Step 7: Model Testing
# Make predictions on the test set
predictions = model.predict(X_test)

# Step 8: Inspect Predictions
# Create a DataFrame to view predictions alongside actual prices
results = pd.DataFrame(
    {'Actual Price': y_test, 'Predicted Price': predictions})
print("Sample Predictions:")
print(results.head(10))  # View the first 10 results

# Step 9: Calculate Evaluation Metrics
mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
print(f'Mean Absolute Error (MAE): {mae}')
print(f'Root Mean Squared Error (RMSE): {rmse}')

# Step 10: Visualize Actual vs. Predicted Prices
# plt.figure(figsize=(10, 6))
# plt.scatter(range(len(y_test)), y_test, color='blue', label='Actual Prices')
# plt.scatter(range(len(predictions)), predictions,
#             color='red', label='Predicted Prices')
# plt.title("Actual vs Predicted Prices")
# plt.xlabel("Sample Index")
# plt.ylabel("Price")
# plt.legend()
# plt.show()

# Step 11: Save the Model and Label Encoder
joblib.dump(X.columns, 'trained_columns.pkl')
joblib.dump(model, 'house_price_model.pkl')
joblib.dump(label_encoder, 'location_label_encoder.pkl')
print("Model and label encoder saved.")

# Step 12: Make a Prediction for a Specific Property
# Define input features for a 2-bedroom, 3-bathroom apartment in a specific location
# Use the label encoder to transform the location name to its integer label
location_name = 'Windsor'  # Example location
encoded_location = label_encoder.transform([location_name])[0]

input_data = {
    'Bedrooms': 2,
    'Bathrooms': 3,
    'Location': encoded_location
}

# Convert input_data to DataFrame with the same column order as X
input_df = pd.DataFrame([input_data], columns=X.columns)

# Load the saved model (optional, for confirmation purposes)
model = joblib.load('house_price_model.pkl')

# Make prediction
predicted_price = model.predict(input_df)[0]
print(
    f'Predicted Price for a 2-bedroom, 3-bathroom apartment in {location_name}: ${predicted_price:,.2f}')
