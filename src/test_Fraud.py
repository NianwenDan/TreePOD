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
    file_names = ["Fraud_X_train.csv", "Fraud_y_train.csv", "Fraud_X_test.csv", "Fraud_y_test.csv"]

    # Check if all files exist
    all_files_exist = all(os.path.exists(os.path.join(path, file)) for file in file_names)

    if all_files_exist:
        # Load the CSV files as DataFrames
        X_train = pd.read_csv(os.path.join(path, "Fraud_X_train.csv"))
        y_train = pd.read_csv(os.path.join(path, "Fraud_y_train.csv"))['isFraud']
        X_test = pd.read_csv(os.path.join(path, "Fraud_X_test.csv"))
        y_test = pd.read_csv(os.path.join(path, "Fraud_y_test.csv"))['isFraud']
        return X_train, y_train, X_test, y_test

def dataProcessing_Fraud(df, categorical_columns):
    # For numeric columns, fill missing values with the median
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())

    # For categorical columns, fill missing values with the mode (most frequent value)
    for col in categorical_columns:
        df[col] = df[col].str.strip()
        df[col] = df[col].fillna(df[col].mode()[0])

    # Apply one-hot encoding to categorical columns
    categorical_df = pd.get_dummies(df[[col for col in categorical_columns]])  # Exclude the target column

    # Combine numerical and encoded categorical data
    X = pd.concat([df[numeric_columns], categorical_df], axis=1) 
    #X.columns = [col[:-1] if col.endswith('.') else col for col in X.columns]

    # Step 4: Encode the target variable   
    y = df['isFraud']
    return X, y

def mainDataProcessing_Fraud(path, dataProcessing_UCI, categorical_columns):
    # Drop the high correlated column "relationship"
    combined_df = pd.read_csv(os.path.join(path, 'onlinefraud.csv')).drop(['nameOrig', 'nameDest'], axis=1)

    X, y = dataProcessing_Fraud(combined_df, categorical_columns)

    # Split back into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=50)

    X_train.to_csv(os.path.join(path, "Fraud_X_train.csv"), index=False)
    y_train.to_csv(os.path.join(path, "Fraud_y_train.csv"), index=False)
    X_test.to_csv(os.path.join(path, "Fraud_X_test.csv"), index=False)
    y_test.to_csv(os.path.join(path, "Fraud_y_test.csv"), index=False)

    return X_train, y_train, X_test, y_test

# Check and load data
categorical_columns = ['type']
path = 'datasets/'

result = check_and_load_data(path)
if result:
    X_train, y_train, X_test, y_test = result
else:
    X_train, y_train, X_test, y_test = mainDataProcessing_Fraud(path, dataProcessing_Fraud, categorical_columns)

# key: column names in df; value: corresponding column names in X_train and X_test
column_mapping = {original: [col for col in X_train.columns if col.startswith(original)]
        for original in categorical_columns} | {original: [original] for original in X_train.select_dtypes(include=[np.number]).columns}
print ('column_mapping: ', column_mapping)

# User-defined config
# user_config = decisionTreeConfig(max_depth_range=range(1, 7), random_state_range=range(50, 51), total_samples=1000)
user_config = decisionTreeConfig()
user_config.set_parameters(
    total_samples=10
)
user_config.fill_undefined_parameters_randomly()
print(user_config.get_all_parameter())

# Generate decision tree candidates
generator = decisionTreeCandidateGenerator(X_train, y_train, X_test, y_test, column_mapping, config=user_config)
generator.train()

# It's ok just override the original file, too many old files make it harder to understand what are they doing.
# Output to json. Vis will load json data
output = generator.trees_info()
output = {
    "code": 200,
    "data": output,
    "msg": "OK",
    "userId": "f6a411d5-988d-4c21-9700-0418482b6fac"
}
print (output)
'''
with open('../example/api/model/trees.json', 'w') as json_file:
    json.dump(output, json_file, indent=4)

# with open('../example/api/model/trees.json', 'r') as json_file:
#     output =  json.load(json_file)
# # Output all Pareto-optimal trees' hierarchy data for creating treemaps
# pareto_tree_id = list(set(value for value_list in output["data"]['pareto_front'].values() for value in value_list))
# print (pareto_tree_id)
hierarchy_data = generator.get_pareto_hierarchy_data()
hierarchy_data = {
    "code": 200,
    "data": hierarchy_data,
    "msg": "OK",
    "userId": "f6a411d5-988d-4c21-9700-0418482b6fac"
}
with open('../example/api/tree/hierarchy_data.json', 'w') as json_file:
    json.dump(hierarchy_data, json_file, indent=4)

# Output the last Pareto-optimal tree
tree_output = generator.tree_structure(int(output['data']['pareto_front']['f1_score__number_of_nodes'][-1]))
tree_output = {
    "code": 200,
    "data": tree_output,
    "msg": "OK",
    "userId": "f6a411d5-988d-4c21-9700-0418482b6fac"
}
with open('../example/api/tree/structure.json', 'w') as json_file:
    json.dump(tree_output, json_file, indent=4)

# Output the last Pareto-optimal tree confusion matrix
tree_confusion_matrix = generator.get_confusion_matrix(int(output['data']['pareto_front']['f1_score__number_of_nodes'][-1]))
tree_confusion_matrix = {
    "code": 200,
    "data": tree_confusion_matrix,
    "msg": "OK",
    "userId": "f6a411d5-988d-4c21-9700-0418482b6fac"
}
with open('../example/api/tree/confusion-matrix.json', 'w') as json_file:
    json.dump(tree_confusion_matrix, json_file, indent=4)'''