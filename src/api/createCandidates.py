import random
import numpy as np
import pandas as pd
import json
from sklearn.model_selection import train_test_split

from decisionTreeCandidateGenerator import decisionTreeCandidateGenerator
from decisionTreeConfig import decisionTreeConfig

# Main
if __name__ == "__main__":
    # Data loading
    df = pd.read_csv('diabetes.csv')
    X = df.drop('Outcome', axis=1).values
    y = df['Outcome'].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)

    # User-defined config
    user_config = decisionTreeConfig(max_depth_range=range(1, 7), random_state_range=range(50, 51), total_samples=300)

    # Generate decision tree candidates
    generator = decisionTreeCandidateGenerator(X_train, y_train, X_test, y_test, config=user_config)
    generator.train()

    with open('decision_tree_candidates.json', 'w') as json_file:
        json.dump(generator.trees_info(is_grouped_by_nodes=True), json_file, indent=4)