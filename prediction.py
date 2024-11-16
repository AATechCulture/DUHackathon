from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import mean_squared_error

app = Flask(__name__, template_folder='prediction_templates')
CORS(app)

def preprocess_data(data_csv):
    # Simulated data processing for demo purposes
    data = pd.DataFrame({
        'Year': range(2008, 2013),
        'Predicted_Annual_Rainfall': [24.187164, 31.677143, 36.456027, 29.176055, 32.601944],
        'Flood_1yr': ['No', 'No', 'No', 'Yes', 'No'],
        'Flood_2yr': ['No', 'No', 'Yes', 'No', 'No'],
        'Flood_3yr': ['No', 'No', 'No', 'No', 'Yes'],
        'Flood_4yr': ['No', 'Yes', 'No', 'No', 'No'],
        'Flood_5yr': ['Yes', 'No', 'No', 'Yes', 'No']
    })
    return data

def get_risk_level(rainfall):
    if rainfall < 35:
        return "Low"
    elif rainfall < 50:
        return "Medium"
    else:
        return "High"

@app.route('/')
def index():
    return render_template('prediction.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    start_year = int(data.get('start_year', 2008))

    # Process the data and generate predictions
    predictions = preprocess_data('demo_data.csv')

    # Filter predictions based on start year
    filtered_predictions = predictions[predictions['Year'] >= start_year].head()

    # Format the results
    results = []
    for _, row in filtered_predictions.iterrows():
        risk_level = get_risk_level(row['Predicted_Annual_Rainfall'])
        result = {
            'year': int(row['Year']),
            'predicted_rainfall': float(row['Predicted_Annual_Rainfall']),
            'risk_level': risk_level,
            'flood_predictions': {
                '1_year': row['Flood_1yr'],
                '2_year': row['Flood_2yr'],
                '3_year': row['Flood_3yr'],
                '4_year': row['Flood_4yr'],
                '5_year': row['Flood_5yr']
            }
        }
        results.append(result)

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
