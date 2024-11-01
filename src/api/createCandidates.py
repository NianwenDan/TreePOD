import random
import numpy as np
import pandas as pd
import json
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from decisionTreeTrainer import decisionTreeTrainer

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

class DecisionTreeCandidateGenerator:
    def __init__(self, X_train, y_train, X_test, y_test, config=None):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.config = config if config is not None else DecisionTreeConfig()
        self.num_candidates = self.config.total_samples

    def generate_tree(self):
        candidates = []
        total_features = self.X_train.shape[1]
        for i in range(self.num_candidates):
            params = self.config.sample_parameters(total_features)
            feature_subset = self.sample_feature_subset(params['nr_of_nodes'])
            tree = decisionTreeTrainer(tree_id = i, 
                                        X_train=self.X_train, 
                                        y_train=self.y_train, 
                                        X_test=self.X_test,
                                        y_test=self.y_test,
                                        feature_subset=feature_subset
                                        )
            tree.train(
                criterion=params['criterion'],
                max_depth=params['max_depth'],
                min_samples_split=params['min_samples_split'],
                random_state=params['random_state'],
                ccp_alpha=params['ccp_alpha']
                )
            candidates.append((tree, feature_subset))
        return candidates

    def sample_feature_subset(self, subset_size):
        total_features = self.X_train.shape[1]
        return random.sample(range(total_features), subset_size)

class DecisionTreeOutput:
    def __init__(self, candidates):
        self.candidates = candidates

    def generate_output(self):
        candidate_info = []
        for tree, feature_subset in self.candidates:
            candidate_info.append({
                'tree_id': tree.id(),
                'params': tree.train_params(),
                'predicted': tree.predict(),
                'number_of_nodes': tree.tree_number_of_nodes()
            })

        output = {
            'total_candidates_before_pruning': len(self.candidates),
            'total_candidates_after_pruning': len([tree for (tree, _) in self.candidates if tree.tree_number_of_nodes() > 1]),
            # 'grouped_by_number_of_nodes': self.group_candidates_by_nodes(candidate_info),
            'candidates': candidate_info
        }

        with open('decision_tree_candidates.json', 'w') as json_file:
            json.dump(output, json_file, indent=4)

    # def group_candidates_by_nodes(self, candidate_info):
    #     grouped = {}
    #     for candidate in candidate_info:
    #         num_nodes = candidate['number_of_nodes']
    #         if num_nodes not in grouped:
    #             grouped[num_nodes] = []
    #         grouped[num_nodes].append(candidate)
    #     return grouped

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
    generator = DecisionTreeCandidateGenerator(X_train, y_train, X_test, y_test, config=user_config)
    candidates = generator.generate_tree()

    # Output to json. Vis will load json data
    output = DecisionTreeOutput(candidates, X_test, y_test)
    output.generate_output()