import random
import numpy as np
import pandas as pd
import json
from sklearn.model_selection import train_test_split

from decisionTreeCandidateGenerator import decisionTreeCandidateGenerator


# Module 1: Configuration and Parameters
class DecisionTreeConfig:
    def __init__(self, criterion_options=None, max_depth_range=None, min_samples_split_range=None, random_state_range=None, ccp_alpha_range=None, total_samples=100):
        self.criterion_options = criterion_options if criterion_options is not None else ['gini', 'entropy', 'log_loss']
        self.max_depth_range = max_depth_range if max_depth_range is not None else range(1, 11)
        self.min_samples_split_range = min_samples_split_range if min_samples_split_range is not None else range(2, 11)
        self.random_state_range = random_state_range if random_state_range is not None else range(0, 100)
        self.ccp_alpha_range = ccp_alpha_range if ccp_alpha_range is not None else np.linspace(0.0, 0.05, 10)
        self.total_samples = total_samples

    def sample_parameters(self, total_features):
        criterion = random.choice(self.criterion_options)
        max_depth = random.choice(self.max_depth_range)
        min_samples_split = random.choice(self.min_samples_split_range)
        random_state = random.choice(self.random_state_range)
        nr_of_nodes = random.randint(1, total_features)
        ccp_alpha = random.choice(self.ccp_alpha_range)
        return {
            'criterion': criterion,
            'max_depth': max_depth,
            'min_samples_split': min_samples_split,
            'random_state': random_state,
            'nr_of_nodes': nr_of_nodes,
            'ccp_alpha': ccp_alpha # TODO: add another input to activate/deactivate pruning
        }

# Main
if __name__ == "__main__":
    # Data loading
    df = pd.read_csv('diabetes.csv')
    X = df.drop('Outcome', axis=1).values
    y = df['Outcome'].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)

    # User-defined config
    user_config = DecisionTreeConfig(max_depth_range=range(1, 7), random_state_range=range(50, 51), total_samples=300)

    # Generate decision tree candidates
    generator = decisionTreeCandidateGenerator(X_train, y_train, X_test, y_test, config=user_config)
    generator.train()

    with open('decision_tree_candidates.json', 'w') as json_file:
        json.dump(generator.candidates(is_grouped_by_nodes=True), json_file, indent=4)