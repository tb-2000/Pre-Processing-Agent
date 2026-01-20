class DataCleaning:
    """
    A class to clean police data
    """
def clean_data(data_raw):
    import pandas as pd
    import numpy as np
    from sklearn.impute import SimpleImputer
    from datetime import datetime
    
    # Create a copy to avoid modifying the original data
    data = data_raw.copy()
    
    # Step 1: Remove columns with more than 40% missing values
    # county_name has 100% missing and search_type has 96.52% missing
    data = data.drop(columns=['county_name', 'search_type'])
    
    # Step 2: Convert stop_date and stop_time to datetime objects
    data['stop_date'] = pd.to_datetime(data['stop_date'])
    # Keep stop_time as string for now to avoid the datetime.combine error
    
    # Step 3: Remove outliers in driver_age and driver_age_raw using 3*IQR rule
    for col in ['driver_age', 'driver_age_raw']:
        Q1 = data[col].quantile(0.25)
        Q3 = data[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR
        data = data[(data[col] >= lower_bound) & (data[col] <= upper_bound)]
    
    # Step 4: Impute missing values
    # Numeric columns: driver_age and driver_age_raw
    numeric_imputer = SimpleImputer(strategy='mean')
    data['driver_age'] = numeric_imputer.fit_transform(data[['driver_age']]).ravel()
    data['driver_age_raw'] = numeric_imputer.fit_transform(data[['driver_age_raw']]).ravel()
    
    # Categorical columns: driver_gender, driver_race, violation_raw, violation, stop_outcome, stop_duration
    categorical_imputer = SimpleImputer(strategy='most_frequent')
    categorical_cols = ['driver_gender', 'driver_race', 'violation_raw', 'violation', 'stop_outcome', 'stop_duration']
    data[categorical_cols] = categorical_imputer.fit_transform(data[categorical_cols])
    
    # Step 5: Remove duplicate rows
    data = data.drop_duplicates()
    
    # Step 6: Remove rows with remaining missing values (if any)
    data = data.dropna()
    
    # Step 7: Check consistency between driver_age_raw and driver_age
    # Calculate expected age from driver_age_raw (assuming current year is 2026)
    expected_age = 2026 - data['driver_age_raw']
    # Identify inconsistencies
    inconsistent = np.abs(data['driver_age'] - expected_age) > 5  # Allow 5-year tolerance
    # Resolve by using driver_age (already cleaned) and marking driver_age_raw as categorical
    data.loc[inconsistent, 'driver_age_raw'] = -1  # Mark as invalid
    data['driver_age_raw'] = data['driver_age_raw'].astype('category')
    
    # Step 8: Combine stop_date and stop_time into a single datetime column
    # Fixed: Using pd.to_datetime with string concatenation instead of pd.datetime.combine
    data['stop_datetime'] = pd.to_datetime(data['stop_date'].astype(str) + ' ' + data['stop_time'])
    data = data.drop(columns=['stop_date', 'stop_time'])  # Remove original columns
    
    # Step 9: Convert stop_duration from string to numeric representation
    duration_mapping = {
        '0-15 Min': 7.5,
        '16-30 Min': 23,
        '30+ Min': 45
    }
    data['stop_duration_minutes'] = data['stop_duration'].map(duration_mapping)
    data = data.drop(columns=['stop_duration'])  # Remove original column
    
    # Step 10: Validate logical relationships between columns
    # Check if is_arrested is consistent with stop_outcome
    arrest_outcome_inconsistency = (
        (data['is_arrested'] == True) & 
        (data['stop_outcome'] != 'Arrest Driver')
    )
    # Check if search_conducted aligns with non-null search_type (but search_type was removed)
    # This check is no longer applicable after removing search_type
    
    # Mark inconsistent arrest outcomes for review
    if arrest_outcome_inconsistency.any():
        data['arrest_inconsistency'] = arrest_outcome_inconsistency
    else:
        data['arrest_inconsistency'] = False
    
    return data

if __name__ == "__main__":
    import pandas as pd

    # Example usage
    data_raw = pd.read_csv("police_project.csv")
    data_cleaned = clean_data(data_raw)
    data_cleaned.to_csv("police_project_cleaned.csv", index=False)
