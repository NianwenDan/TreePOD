from decisionTreeCandidateGenerator import decisionTreeCandidateGenerator
from decisionTreeConfig import decisionTreeConfig
import pandas as pd
from sklearn.model_selection import train_test_split
import json, os


df = pd.read_csv('diabetes.csv')
X = df.drop('Outcome', axis=1)
y = df['Outcome']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)
# User-defined config
user_config = decisionTreeConfig(max_depth_range=range(1, 7), random_state_range=range(50, 51), total_samples=300)
dt_generator = decisionTreeCandidateGenerator(X_train, y_train, X_test, y_test, config=user_config)

dt_generator.train()

output = dt_generator.trees_info()


# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
with open('decision_tree_candidates.json', 'w') as json_file:
    json.dump(output, json_file, indent=4)