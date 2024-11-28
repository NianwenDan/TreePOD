import random
import numpy as np
import pandas as pd
import json
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from decisionTreeConfig import decisionTreeConfig
from decisionTreeCandidateGenerator import decisionTreeCandidateGenerator

# Data loading
'''
df = pd.read_csv('diabetes.csv')
X = df.drop('Outcome', axis=1).values
y = df['Outcome'].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=100)
'''
df = pd.read_csv('src/api/datasets/uci_adult.data.csv').drop('relationship', axis=1)
# Step 2: Clean categorical data
categorical_columns = [
    'workclass', 'education', 'occupation',
    'race', 'sex', 'native-country', 'income'
]

for col in categorical_columns:
    df[col] = df[col].str.strip()

# Step 3: Handle missing values
# For numeric columns, fill missing values with the median
numeric_columns = df.select_dtypes(include=[np.number]).columns
df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())

# For categorical columns, fill missing values with the mode (most frequent value)
for col in categorical_columns:
    df[col] = df[col].fillna(df[col].mode()[0])

# Step 5: Split categorical and numerical columns
# Apply one-hot encoding to categorical columns
categorical_df = pd.get_dummies(df[[col for col in categorical_columns if col != 'marital-status']])  # Exclude the target column

# Combine numerical and encoded categorical data
X = pd.concat([df[numeric_columns], categorical_df], axis=1) 

# Step 4: Encode the target variable   
y = df['marital-status'].map({' Never-married': 1, ' Married-civ-spouse': 0, ' Married-spouse-absent': 0, ' Married-AF-spouse': 0, ' Divorced': 2, ' Separated': 2, ' Widowed': 3})
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=100)
column_mapping = {original: [col for col in X_train.columns if col.startswith(original)]
        for original in categorical_columns}
for key in numeric_columns:
    column_mapping[key] = [] + [key]

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