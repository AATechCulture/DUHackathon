import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import numpy as np
import pandas as pd
import sklearn as sk
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, recall_score, roc_auc_score, confusion_matrix, mean_squared_error


def preprocess_data(input_file_path):
    # Read the dataset
    data = pd.read_csv(input_file_path,header=None)
    

    # Assign the first row as column headers
    data.columns = data.iloc[0]
    data = data[1:].reset_index(drop=True)  # Drop the first row and reset the index

    # Create labels for 1–5 year predictions using the 'Flood' column
    for i in range(1, 6):  # 1 to 5 years
        data[f'Flood_{i}yr'] = data['Flood'].shift(-i)

    # Drop rows with NaN values due to shifting
    data = data.dropna().reset_index(drop=True)

    # Ensure the 'Flood' column is encoded as 'Yes'/'No'
    label_encoder = LabelEncoder()
    data['Flood'] = label_encoder.fit_transform(data['Flood'])  # Encode 'Yes'/'No'

    # Handle TF-IDF Vectorization for a specific column (e.g., 'Subdivision')
    if 'Subdivision' in data.columns:
        vectorizer = TfidfVectorizer()
        vectorized = vectorizer.fit_transform(data['Subdivision'].astype(str))
    
        # Convert sparse matrix to dense DataFrame and merge
        vectorized_df = pd.DataFrame(vectorized.toarray(), columns=vectorizer.get_feature_names_out())
        data = pd.concat([vectorized_df, data.drop(columns=['Subdivision'])], axis=1)

    # Convert all column names to strings for compatibility
    data.columns = data.columns.astype(str)

    # Display the updated DataFrame
    print(data.head())

    # Save the updated DataFrame for reference
    data.to_csv('processed_data.csv', index=False)

    data['Flood'].replace(['Yes', 'No'], [1, 0], inplace=True)
    data.replace(['NA'],[0],inplace=True)



    # Select numerical columns for scaling
    numerical_columns = data.select_dtypes(include=['float64', 'int64']).columns
    x = data[numerical_columns]

    # Apply MinMax scaling to numerical features
    minmax = MinMaxScaler(feature_range=(0, 1))
    x_scaled = minmax.fit_transform(x)

    # Replace the numerical columns with scaled values
    data[numerical_columns] = x_scaled

    # Save the processed data for reference
    data.to_csv('processed_data_corrected.csv', index=False)

    # Display a preview of the processed DataFrame
    print(data.head())

    


def flood_prediction(prediction_input,prediction_output,start_year):
    # Load the processed data
    data = pd.read_csv(prediction_input)

    # Encode flood columns ('Yes'/'No') to numerical values for each flood return period
    label_encoder = LabelEncoder()
    for i in range(1, 6):
        data[f'Flood_{i}yr'] = label_encoder.fit_transform(data[f'Flood_{i}yr'])

    # Predictions dictionary to store results
    predictions = {}

    # Choose a range of years to predict (2008 to 2012)
    end_year = start_year + 5
    years_to_predict = range(start_year, end_year)  # Predict for years 2008-2012 #CHANGE TO USER INPUT

    # Features and target for regression (rainfall)
    x_rainfall = data.drop(columns=['Year', 'Annual'] + [f'Flood_{i}yr' for i in range(1, 6)])
    y_rainfall = data['Annual']

    # Train-Test Split for rainfall prediction
    x_rainfall_train, x_rainfall_test, y_rainfall_train, y_rainfall_test = train_test_split(
        x_rainfall, y_rainfall, test_size=0.2, random_state=42
    )

    # Train a regression model for annual rainfall prediction
    rainfall_model = RandomForestRegressor(max_depth=5, random_state=1)
    rainfall_model.fit(x_rainfall_train, y_rainfall_train)

    # Predict annual rainfall for the entire dataset (to use for future years)
    rainfall_pred = rainfall_model.predict(x_rainfall_test)

    # Evaluate rainfall predictions
    rainfall_rmse = np.sqrt(mean_squared_error(y_rainfall_test, rainfall_pred))
    print(f"Rainfall Prediction RMSE: {rainfall_rmse:.2f}")

    # Prepare an empty list to store the predictions for the CSV
    results = []

    # Loop through years to predict rainfall and flooding for each year
    for year in years_to_predict:
        # Get the data for the specific year (remove target variables for flood prediction)
        specific_year_data = data[data['Year'] == year].drop(
            columns=[f'Flood_{i}yr' for i in range(1, 6)] + ['Year', 'Annual']
        )
    
        # Predict annual rainfall for the specific year
        rainfall_specific_year = rainfall_model.predict(specific_year_data)
        predicted_rainfall = rainfall_specific_year[0]

        # Store the result for predicted rainfall
        result = {'Year': year, 'Predicted_Annual_Rainfall': predicted_rainfall}

        # Loop to predict the flood possibilities for each flood return period (1yr, 2yr, ..., 5yr)
        for i in range(1, 6):
            # Prepare the data for flood prediction for the specific year
            flood_data = data[data['Year'] == year].drop(columns=['Year', 'Annual'] + [f'Flood_{j}yr' for j in range(1, 6)])

            # Include the predicted rainfall as a feature for flooding prediction
            flood_data['Predicted_Rainfall'] = predicted_rainfall

            y_flood = data[data['Year'] == year][f'Flood_{i}yr']
        
            # If there's only one sample, don't split and directly use the data
            if len(flood_data) > 1:
                x_train, x_test, y_train, y_test = train_test_split(flood_data, y_flood, test_size=0.2, random_state=42)
            
                # Train a Random Forest model for flooding prediction
                flood_model = RandomForestClassifier(max_depth=5, random_state=1)
                flood_model.fit(x_train, y_train)

                # Make predictions for the test set (for evaluation)
                y_pred = flood_model.predict(x_test)

                # Save the flood predictions as well
                result[f'Flood_{i}yr'] = label_encoder.inverse_transform(y_pred)[0]
            else:
                # Directly predict the flood occurrence for this year with the single sample
                flood_model = RandomForestClassifier(max_depth=5, random_state=1)
                flood_model.fit(flood_data, y_flood)
                y_pred_specific_year = flood_model.predict(flood_data)
                result[f'Flood_{i}yr'] = label_encoder.inverse_transform(y_pred_specific_year)[0]

        # Append the result for the specific year
        results.append(result)

    # Convert the results into a DataFrame
    results_df = pd.DataFrame(results)

    # Save the results DataFrame to a CSV file
    results_df.to_csv(prediction_output, index=False)

    # Print the DataFrame to verify
    print("\nPredictions saved to 'flood_and_rainfall_predictions_2008_2012.csv':")
    print(results_df)





if __name__ == '__main__':

    input_file_path = '/Users/raygantaylor/Desktop/BESMART_files/Austin_Rainfall_95.csv'
    prediction_input = 'processed_data_corrected.csv' 
    prediction_output = 'flood_and_rainfall_predictions_2008_2012.csv' # need better naming conventions
    start_year = 2008
    
    print(f"Input file path: {input_file_path}")
    print(f"Prediction input file path: {prediction_input}")
    print(f"Prediction output file path: {prediction_output}")

    preprocess_data(input_file_path)
    flood_prediction(prediction_input,prediction_output,start_year)


    '''
    HOW TO INTERPRET TERMINAL OUTPUT/CSV:
    Only consider the possibility of a flood for the first year. For example, 
    to determine whether a flood would occur 1 - 5 years after 2008, only read the first row:
     Year  Predicted_Annual_Rainfall Flood_1yr Flood_2yr Flood_3yr Flood_4yr Flood_5yr
0  2008                  24.187164        No        No        No        No       Yes
1  2009                  31.677143        No        No        No       Yes        No

    To determine the level of risk (low, medium, high) for a specific year:
    consider all values in the Predicted_Annual_Rainfall column. For example:

    Year  Predicted_Annual_Rainfall Flood_1yr Flood_2yr Flood_3yr Flood_4yr Flood_5yr
0  2008                  24.187164       
1  2009                  31.677143       
2  2010                  36.456027       
3  2011                  29.176055      
4  2012                  32.601944 

    We calculated the mean, median, minimum, and maximum rainfall when Flood == 'Yes' and Flood == 'No'
    Based on those results for this dataset, (measurements in mm)
    if predicted annual rainfall < 35, flood risk is low
    if predicted annual rainfall 35 < x < 50, flood risk is medium
    if predicited annual rainfall > 50, flood risk is high

    The Austin_Rainfall_95 dataset was created manually, however, the data is from NOAA.
    '''