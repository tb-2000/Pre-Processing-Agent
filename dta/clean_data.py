def clean_data(data_raw):
    import pandas as pd
    import numpy as np
    from sklearn.impute import SimpleImputer

    # Step 1: Remove the `county_name` column (100% missing)
    data_cleaned = data_raw.drop(columns=['county_name'])

    # Step 2: Convert `stop_date` and `stop_time` to datetime
    data_cleaned['stop_date'] = pd.to_datetime(data_cleaned['stop_date'])
    data_cleaned['stop_time'] = pd.to_datetime(data_cleaned['stop_time'], format='%H:%M').dt.time
    data_cleaned['stop_datetime'] = pd.to_datetime(data_cleaned['stop_date'].dt.strftime('%Y-%m-%d') + ' ' + 
                                                   data_cleaned['stop_time'].astype(str))

    # Step 3: Reconstruct `driver_age` from `driver_age_raw` and `stop_date`
    # Extract year from stop_date
    current_year = data_cleaned['stop_date'].dt.year
    data_cleaned['driver_age'] = current_year - data_cleaned['driver_age_raw']

    # Step 4: Drop `driver_age_raw` as it's now redundant
    data_cleaned = data_cleaned.drop(columns=['driver_age_raw'])

    # Step 5: Impute missing values in categorical columns using mode
    categorical_columns = ['driver_gender', 'driver_race', 'violation_raw', 'violation', 
                           'stop_outcome', 'is_arrested', 'stop_duration']
    
    for col in categorical_columns:
        if data_cleaned[col].isnull().sum() > 0:
            mode_value = data_cleaned[col].mode()
            if len(mode_value) > 0:
                data_cleaned[col].fillna(mode_value[0], inplace=True)

    # Step 6: Remove `search_type` column (96.52% missing)
    data_cleaned = data_cleaned.drop(columns=['search_type'])

    # Step 7: Ensure `search_conducted` and `drugs_related_stop` are boolean
    data_cleaned['search_conducted'] = data_cleaned['search_conducted'].astype(bool)
    data_cleaned['drugs_related_stop'] = data_cleaned['drugs_related_stop'].astype(bool)

    # Step 8: Standardize categorical columns (uppercase, strip whitespace)
    for col in ['driver_gender', 'driver_race', 'violation_raw', 'violation', 
                'stop_outcome', 'stop_duration']:
        data_cleaned[col] = data_cleaned[col].str.strip().str.upper()

    # Step 9: Handle `stop_duration` as ordinal categorical
    duration_mapping = {
        "0-15 MIN": 10,
        "16-30 MIN": 20,
        "30+ MIN": 35,
        "0-15 Min": 10,
        "16-30 Min": 20,
        "30+ Min": 35
    }
    data_cleaned['stop_duration'] = data_cleaned['stop_duration'].map(duration_mapping)
    # Convert to numeric type
    data_cleaned['stop_duration'] = pd.to_numeric(data_cleaned['stop_duration'], errors='coerce')

    # Step 10: Remove duplicate rows
    data_cleaned = data_cleaned.drop_duplicates()

    # Step 11: Remove rows with extreme outliers in `driver_age`
    Q1 = data_cleaned['driver_age'].quantile(0.25)
    Q3 = data_cleaned['driver_age'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 3 * IQR
    upper_bound = Q3 + 3 * IQR
    data_cleaned = data_cleaned[(data_cleaned['driver_age'] >= lower_bound) & 
                                (data_cleaned['driver_age'] <= upper_bound)]

    # Step 12: Validate data consistency between `driver_age` and `driver_age_raw` (already done via reconstruction)
    # No need for further action since we reconstructed `driver_age` from `driver_age_raw`

    # Step 13: Final cleanup: reset index
    data_cleaned = data_cleaned.reset_index(drop=True)

    return data_cleaned