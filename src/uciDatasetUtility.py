import numpy as np
import pandas as pd
import os


def check_and_load_data(path):
    """
    Check if required CSV files exist in the given path and load them as DataFrames.
    If any file is missing, call the data processing function.
    """
    # File names
    file_names = ["UCI_X_train.csv", "UCI_y_train.csv", "UCI_X_test.csv", "UCI_y_test.csv"]

    # Check if all files exist
    all_files_exist = all(os.path.exists(os.path.join(path, file)) for file in file_names)

    if all_files_exist:
        # Load the CSV files as DataFrames
        X_train = pd.read_csv(os.path.join(path, "UCI_X_train.csv"))
        y_train = pd.read_csv(os.path.join(path, "UCI_y_train.csv"))['marital-status']
        X_test = pd.read_csv(os.path.join(path, "UCI_X_test.csv"))
        y_test = pd.read_csv(os.path.join(path, "UCI_y_test.csv"))['marital-status']
        return X_train, y_train, X_test, y_test

def dataProcessing_UCI(df, categorical_columns):
    # For numeric columns, fill missing values with the median
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())

    # For categorical columns, fill missing values with the mode (most frequent value)
    for col in categorical_columns:
        df[col] = df[col].str.strip()
        df[col] = df[col].fillna(df[col].mode()[0])
    if "income" in df.columns:
        df["income"] = df["income"].str.rstrip(".")

    # Apply one-hot encoding to categorical columns
    categorical_df = pd.get_dummies(df[[col for col in categorical_columns if col != 'marital-status']])  # Exclude the target column

    # Combine numerical and encoded categorical data
    X = pd.concat([df[numeric_columns], categorical_df], axis=1) 
    X.columns = [col[:-1] if col.endswith('.') else col for col in X.columns]

    # Step 4: Encode the target variable   
    y = df['marital-status'].map({' Never-married': 1, ' Married-civ-spouse': 0, ' Married-spouse-absent': 0, ' Married-AF-spouse': 0, ' Divorced': 2, ' Separated': 2, ' Widowed': 3})
    return X, y

def mainDataProcessing_UCI(path, dataProcessing_UCI, categorical_columns):
    # Drop the high correlated column "relationship"
    df_train = pd.read_csv(os.path.join(path, 'uci_adult.data.csv')).drop('relationship', axis=1)
    df_test = pd.read_csv(os.path.join(path, 'uci_adult.test.csv')).drop('relationship', axis=1)
    
    df_train['is_train'] = True
    df_test['is_train'] = False
    combined_df = pd.concat([df_train, df_test], axis=0)

    X_combined, y_combined = dataProcessing_UCI(combined_df, categorical_columns)

    # Split back into training and testing sets
    X_train = X_combined[combined_df['is_train']]
    y_train = y_combined[combined_df['is_train']]
    X_test = X_combined[~combined_df['is_train']]
    y_test = y_combined[~combined_df['is_train']]

    X_train.to_csv(os.path.join(path, "UCI_X_train.csv"), index=False)
    y_train.to_csv(os.path.join(path, "UCI_y_train.csv"), index=False)
    X_test.to_csv(os.path.join(path, "UCI_X_test.csv"), index=False)
    y_test.to_csv(os.path.join(path, "UCI_y_test.csv"), index=False)

    return X_train, y_train, X_test, y_test


def features_in_dataset():
    return ["age", "workclass", "fnlwgt", "education", "education-num", "marital-status", "occupation", "relationship", "race", "sex", "capital-gain", "capital-loss", "hours-per-week", "native-country", "income"]


def get_decision_tree_candidate_generator_params():
    # Check and load data
    categorical_columns = ['workclass', 'education', 'occupation', 'race', 'sex', 'native-country', 'income']
    path = 'datasets/'

    result = check_and_load_data(path)
    if result:
        X_train, y_train, X_test, y_test = result
    else:
        X_train, y_train, X_test, y_test = mainDataProcessing_UCI(path, dataProcessing_UCI, categorical_columns)

    # key: column names in df; value: corresponding column names in X_train and X_test
    column_mapping = {original: [col for col in X_train.columns if col.startswith(original) and col != 'education-num']
            for original in categorical_columns} | {original: [original] for original in X_train.select_dtypes(include=[np.number]).columns}
    
    return X_train, y_train, X_test, y_test, column_mapping