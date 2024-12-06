import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def check_and_load_data(path):
    """
    Check if required CSV files exist in the given path and load them as DataFrames.
    If any file is missing, call the data processing function.
    """
    # File names
    file_names = ["Fraud_X_train.csv", "Fraud_y_train.csv", "Fraud_X_test.csv", "Fraud_y_test.csv"]

    # Check if all files exist
    all_files_exist = all(os.path.exists(os.path.join(path, file)) for file in file_names)

    if all_files_exist:
        # Load the CSV files as DataFrames
        X_train = pd.read_csv(os.path.join(path, "Fraud_X_train.csv"))
        y_train = pd.read_csv(os.path.join(path, "Fraud_y_train.csv"))['FraudFound_P']
        X_test = pd.read_csv(os.path.join(path, "Fraud_X_test.csv"))
        y_test = pd.read_csv(os.path.join(path, "Fraud_y_test.csv"))['FraudFound_P']
        return X_train, y_train, X_test, y_test

def dataProcessing_Fraud(df, categorical_columns):
    # For numeric columns, fill missing values with the median
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())

    # For categorical columns, fill missing values with the mode (most frequent value)
    for col in categorical_columns:
        df[col] = df[col].str.strip()
        df[col] = df[col].fillna(df[col].mode()[0])

    df['MonthClaimed'] = df['MonthClaimed'].map({'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12, 0: 0})
    df['Month'] = df['Month'].map({'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12})
    df['DayOfWeek'] = df['DayOfWeek'].map({'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7})
    df['DayOfWeekClaimed'] = df['DayOfWeekClaimed'].map({'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7, 0: 0})

    # Apply one-hot encoding to categorical columns
    categorical_df = pd.get_dummies(df[[col for col in categorical_columns]])  # Exclude the target column

    # Combine numerical and encoded categorical data
    X = pd.concat([df[numeric_columns], categorical_df], axis=1) 
    #X.columns = [col[:-1] if col.endswith('.') else col for col in X.columns]

    # Step 4: Encode the target variable   
    y = df['FraudFound_P']
    return X, y

def mainDataProcessing_Fraud(path, dataProcessing_fraud, categorical_columns):
    # Drop the high correlated column "relationship"
    df = pd.read_csv(os.path.join(path, 'fraud_oracle.csv')).drop(['PolicyNumber', 'Age'], axis=1)
    
    X, y = dataProcessing_Fraud(df, categorical_columns)

    # Split back into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=50)

    X_train.to_csv(os.path.join(path, "Fraud_X_train.csv"), index=False)
    y_train.to_csv(os.path.join(path, "Fraud_y_train.csv"), index=False)
    X_test.to_csv(os.path.join(path, "Fraud_X_test.csv"), index=False)
    y_test.to_csv(os.path.join(path, "Fraud_y_test.csv"), index=False)

    return X_train, y_train, X_test, y_test


def get_decision_tree_candidate_generator_params():
    # Check and load data
    categorical_columns = ['Make', 'AccidentArea', 'Sex', 'MaritalStatus', 'Fault', 'PolicyType', 'VehicleCategory', 'VehiclePrice', 
        'Days_Policy_Accident', 'Days_Policy_Claim','PastNumberOfClaims', 'AgeOfVehicle', 'AgeOfPolicyHolder',
        'PoliceReportFiled', 'WitnessPresent', 'AgentType', 'NumberOfSuppliments', 'AddressChange_Claim', 'NumberOfCars', 'BasePolicy']
    path = 'datasets/'

    result = check_and_load_data(path)
    if result:
        X_train, y_train, X_test, y_test = result
    else:
        X_train, y_train, X_test, y_test = mainDataProcessing_Fraud(path, dataProcessing_Fraud, categorical_columns)

    # key: column names in df; value: corresponding column names in X_train and X_test
    column_mapping = {original: [col for col in X_train.columns if col.startswith(original)]
            for original in categorical_columns} | {original: [original] for original in X_train.select_dtypes(include=[np.number]).columns}
    # print ('column_mapping: ', column_mapping)

    return X_train, y_train, X_test, y_test, column_mapping