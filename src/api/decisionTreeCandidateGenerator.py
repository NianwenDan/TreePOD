from decisionTreeTrainer import decisionTreeTrainer
import random


class decisionTreeCandidateGenerator:
    def __init__(self, X_train, y_train, X_test, y_test, config):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.config = config
        self.num_candidates = self.config.total_samples
        self._candidates = None

    def _sample_feature_subset(self, subset_size):
        total_features = self.X_train.shape[1]
        return random.sample(range(total_features), subset_size)

    def train(self):
        candidates = {}
        total_features = self.X_train.shape[1]
        for i in range(self.num_candidates):
            params = self.config.sample_parameters(total_features)
            feature_subset = self._sample_feature_subset(params['nr_of_nodes'])
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
            # save as dict, key = tree id
            candidates[i] = (tree, feature_subset)
            candidates[i] = {
                'tree_object' : tree,
                'feature_subset' : feature_subset
            }
        self._candidates = candidates

    def candidates(self, is_grouped_by_nodes: False):
        candidate_info = []
        for t in self._candidates.values():
            tree = t['tree_object']
            tree_info = {
                'tree_id': tree.id(),
                'params': tree.train_params(),
                'predicted': tree.predict(),
                'number_of_nodes': tree.tree_number_of_nodes()
            }
            candidate_info.append(tree_info)
        
        def group_candidates_by_nodes():
            grouped = {}
            for candidate in candidate_info:
                num_nodes = candidate['number_of_nodes']
                if num_nodes not in grouped:
                    grouped[num_nodes] = []
                grouped[num_nodes].append(candidate)
            grouped = {k: grouped[k] for k in sorted(grouped)}
            return grouped
        
        output = {
            'total_candidates_before_pruning': len(candidate_info),
            'total_candidates_after_pruning': len([info for info in candidate_info if info['number_of_nodes'] > 1]),
            'candidates': candidate_info
        }
        if is_grouped_by_nodes:
            output['candidates'] = group_candidates_by_nodes()
        return output


    