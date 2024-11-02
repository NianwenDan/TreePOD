import random
import numpy as np

class decisionTreeConfig:
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
            'ccp_alpha': ccp_alpha, # TODO: add another input to activate/deactivate pruning
            'total_samples' : self.total_samples
        }