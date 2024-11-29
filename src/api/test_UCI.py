import os
import numpy as np
import pandas as pd
import json
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from decisionTreeConfig import decisionTreeConfig
from decisionTreeCandidateGenerator import decisionTreeCandidateGenerator

def check_and_load_data(path):
    """
    Check if required CSV files exist in the given path and load them as DataFrames.
    If any file is missing, call the data processing function.
    """
    # File names
    file_names = ["X_train.csv", "y_train.csv", "X_test.csv", "y_test.csv"]

    # Check if all files exist
    all_files_exist = all(os.path.exists(os.path.join(path, file)) for file in file_names)

    if all_files_exist:
        # Load the CSV files as DataFrames
        X_train = pd.read_csv(os.path.join(path, "UCI_X_train.csv"))
        y_train = pd.read_csv(os.path.join(path, "UCI_y_train.csv"))
        X_test = pd.read_csv(os.path.join(path, "UCI_X_test.csv"))
        y_test = pd.read_csv(os.path.join(path, "UCI_y_test.csv"))
        return X_train, y_train, X_test, y_test

def dataProcessing_UCI(df, categorical_columns):
    # For numeric columns, fill missing values with the median
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())

    # For categorical columns, fill missing values with the mode (most frequent value)
    for col in categorical_columns:
        df[col] = df[col].str.strip()
        df[col] = df[col].fillna(df[col].mode()[0])

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

    '''
    X_train, y_train = dataProcessing_UCI(df_train, categorical_columns)
    X_test, y_test = dataProcessing_UCI(df_test, categorical_columns)
    '''
    X, y = dataProcessing_UCI(df_train, categorical_columns)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=100)

    X_train.to_csv(os.path.join(path, "UCI_X_train.csv"), index=False)
    y_train.to_csv(os.path.join(path, "UCI_y_train.csv"), index=False)
    X_test.to_csv(os.path.join(path, "UCI_X_test.csv"), index=False)
    y_test.to_csv(os.path.join(path, "UCI_y_test.csv"), index=False)

    return X_train, y_train, X_test, y_test

# Check and load data
categorical_columns = ['workclass', 'education', 'occupation', 'race', 'sex', 'native-country', 'income']
path = 'src/api/datasets/'

result = check_and_load_data(path)
if result:
    X_train, y_train, X_test, y_test = result
else:
    X_train, y_train, X_test, y_test = mainDataProcessing_UCI(path, dataProcessing_UCI, categorical_columns)

# key: column names in df; value: corresponding column names in X_train and X_test
column_mapping = {original: [col for col in X_train.columns if col.startswith(original)]
        for original in categorical_columns} | {original: [original] for original in X_train.select_dtypes(include=[np.number]).columns}

# User-defined config
user_config = decisionTreeConfig(max_depth_range=range(1, 7), random_state_range=range(50, 51), total_samples=1000)

# Generate decision tree candidates
generator = decisionTreeCandidateGenerator(X_train, y_train, X_test, y_test, column_mapping, config=user_config)
generator.train()

# Output to json. Vis will load json data
output = generator.trees_info()
with open('example/api/model/trees.5.json', 'w') as json_file:
    json.dump(output, json_file, indent=4)

# Output the last Pareto-optimal tree
tree_output = generator.tree_structure(int(output['pareto_front']['f1_score_number_of_nodes'][-1]))
with open('example/api/tree/structure.2.json', 'w') as json_file:
    json.dump(tree_output, json_file, indent=4)