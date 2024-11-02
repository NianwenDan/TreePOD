from decisionTreeTrainer import decisionTreeTrainer
import random


class decisionTreeCandidateGenerator:
    def __init__(self, X_train, y_train, X_test, y_test, config):
        self._X_train = X_train
        self._y_train = y_train
        self._X_test = X_test
        self._y_test = y_test
        self._config = config
        self._num_candidates = self._config.total_samples
        self._candidates = None

        self._status = {
            'code' : -1,
            'msg' : 'NOT TRAINED',
            'total_number_of_samples' : self._num_candidates,
            'number_of_samples_trained' : 0
        }


    def _sample_feature_subset(self, subset_size):
        total_features = self._X_train.shape[1]
        return random.sample(range(total_features), subset_size)
    
    def status(self):
        '''
        Return the status of the training process
        
        @return: dict: status of the training process
        '''
        return self._status


    def train(self):
        '''
        Train the decision tree candidates
        
        @return: None
        '''
        self._status['code'] = 1
        self._status['msg'] = 'TRAIN START'
        candidates = {}
        total_features = self._X_train.shape[1]
        for i in range(self._num_candidates):
            params = self._config.sample_parameters(total_features)
            feature_subset = self._sample_feature_subset(params['nr_of_nodes'])
            tree = decisionTreeTrainer(tree_id = i + 1, 
                                        X_train=self._X_train, 
                                        y_train=self._y_train, 
                                        X_test=self._X_test,
                                        y_test=self._y_test,
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
            self._status['number_of_samples_trained'] = i + 1  # keep update current status
        
        self._status['code'] = 0
        self._status['msg'] = 'TRAIN COMPLETED'
        self._candidates = candidates


    def trees_info(self, is_grouped_by_nodes: False):
        '''
        Return the information of the decision tree candidates
        
        @return: dict: information of the decision tree candidates
        '''
        if not self._candidates:
            return None
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
            grouped = {k: grouped[k] for k in sorted(grouped)} # Sort the dic based on key
            return grouped
        
        output = {
            'total_candidates_before_pruning': len(candidate_info),
            'total_candidates_after_pruning': len([info for info in candidate_info if info['number_of_nodes'] > 1]),
            'candidates': candidate_info
        }
        if is_grouped_by_nodes:
            output['candidates'] = group_candidates_by_nodes()
        return output


    def tree_structure(self, tree_id: int) -> dict:
        '''
        Return the structure of the decision tree with the given id
        
        @param tree_id: int: the id of the decision tree
        
        @return: dict: the structure of the decision tree
        '''
        if not self._candidates:
            return None
        return self._candidates[tree_id]['tree_object'].tree_structure()
    
    
    def tree_image(self, tree_id: int, length: int, width: int, dpi: int) -> bytes:
        '''
        Return the image of the decision tree
        
        @param tree_id: int: the id of the decision tree
        @param length: int: the length of the image
        @param width: int: the width of the image
        @param dpi: int: the dpi of the image
        
        @return: bytes: the image of the decision tree
        '''
        if not self._candidates:
            return None
        return self._candidates[tree_id]['tree_object'].tree_img(length, width, dpi)

    