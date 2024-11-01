import random
import numpy as np
import pandas as pd
import json
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

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

# Training: TODO: call Nianwen's code instead
class DecisionTreeTrainer:
    def __init__(self, X_train, y_train, feature_subset=None):
        self.X_train = X_train
        self.y_train = y_train
        self.feature_subset = feature_subset

    def train_tree(self, params):
        # Only use feature_subset
        if self.feature_subset:
            X_train_subset = self.X_train[:, self.feature_subset]
        else:
            X_train_subset = self.X_train
        
        tree = DecisionTreeClassifier(
            criterion=params['criterion'],
            max_depth=params['max_depth'],
            min_samples_split=params['min_samples_split'],
            random_state=params['random_state'],
            ccp_alpha=params['ccp_alpha']
        )
        tree.fit(X_train_subset, self.y_train)
        return tree

class DecisionTreeCandidateGenerator:
    def __init__(self, X_train, y_train, config=None):
        self.X_train = X_train
        self.y_train = y_train
        self.config = config if config is not None else DecisionTreeConfig()
        self.num_candidates = self.config.total_samples

    def generate_tree(self):
        candidates = []
        total_features = self.X_train.shape[1]
        for _ in range(self.num_candidates):
            params = self.config.sample_parameters(total_features)
            feature_subset = self.sample_feature_subset(params['nr_of_nodes'])
            trainer = DecisionTreeTrainer(self.X_train, self.y_train, feature_subset)
            tree = trainer.train_tree(params)
            candidates.append((tree, feature_subset))
        return candidates

    def sample_feature_subset(self, subset_size):
        total_features = self.X_train.shape[1]
        return random.sample(range(total_features), subset_size)

class DecisionTreeOutput:
    def __init__(self, candidates, X_test, y_test):
        self.candidates = candidates
        self.X_test = X_test
        self.y_test = y_test

    def generate_output(self):
        candidate_info = []
        for idx, (tree, feature_subset) in enumerate(self.candidates):
            if feature_subset:
                X_test_subset = self.X_test[:, feature_subset]
            else:
                X_test_subset = self.X_test
            y_pred = tree.predict(X_test_subset)        
            f1 = f1_score(self.y_test, y_pred, average='weighted')
            candidate_info.append({
                'tree_id': idx + 1,
                'params': tree.get_params(),
                'number_of_nodes': tree.tree_.node_count,
                'f1_score': f1
            })

        output = {
            'total_candidates_before_pruning': len(self.candidates),
            'total_candidates_after_pruning': len([tree for (tree, _) in self.candidates if tree.tree_.node_count > 1]),
            'candidates': candidate_info,
            'grouped_by_number_of_nodes': self.group_candidates_by_nodes(candidate_info)
        }

        with open('src/vis/decision_tree_candidates.json', 'w') as json_file:
            json.dump(output, json_file, indent=4)

    def group_candidates_by_nodes(self, candidate_info):
        grouped = {}
        for candidate in candidate_info:
            num_nodes = candidate['number_of_nodes']
            if num_nodes not in grouped:
                grouped[num_nodes] = []
            grouped[num_nodes].append(candidate)
        return grouped

# Main
if __name__ == "__main__":
    # Data loading
    df = pd.read_csv('src/api/diabetes.csv')
    X = df.drop('Outcome', axis=1).values
    y = df['Outcome'].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=100)

    # User-defined config
    user_config = DecisionTreeConfig(max_depth_range=range(1, 7), random_state_range=range(50, 51), total_samples=300)

    # Generate decision tree candidates
    generator = DecisionTreeCandidateGenerator(X_train, y_train, config=user_config)
    candidates = generator.generate_tree()

    # Output to json. Vis will load json data
    output = DecisionTreeOutput(candidates, X_test, y_test)
    output.generate_output()