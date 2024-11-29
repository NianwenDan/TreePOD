from decisionTreeTrainer import decisionTreeTrainer
from paretoAnalysis import paretoAnalysis
import random

class decisionTreeCandidateGenerator:
    def __init__(self, X_train, y_train, X_test, y_test, column_mapping, config):
        self._X_train = X_train
        self._y_train = y_train
        self._X_test = X_test
        self._y_test = y_test
        self._config = config
        self._num_candidates = self._config.total_samples
        self._candidates = None
        self._column_mapping = column_mapping
        self._pareto_front = None

        self._status = {
            'code' : -1,
            'msg' : 'NOT TRAINED',
            'total_number_of_samples' : self._num_candidates,
            'number_of_samples_trained' : 0
        }


    def _sample_feature_subset(self, subset_size):
        total_features = len(self._column_mapping)
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
        total_features = len(self._column_mapping)
        for i in range(self._num_candidates):
            params = self._config.sample_parameters(total_features)
            feature_subset_index = self._sample_feature_subset(params['nr_of_attributes'])
            feature_subset = [list(self._column_mapping.keys())[ii] for ii in feature_subset_index]
            feature_subset_mapped = []
            for ii in feature_subset:
                feature_subset_mapped += self._column_mapping[ii]
            tree_id = i + 1
            tree = decisionTreeTrainer(tree_id = tree_id, 
                                        X_train=self._X_train, 
                                        y_train=self._y_train, 
                                        X_test=self._X_test,
                                        y_test=self._y_test,
                                        feature_subset=feature_subset_mapped
                                        )
            tree.train(
                criterion=params['criterion'],
                max_depth=params['max_depth'],
                min_samples_split=params['min_samples_split'],
                random_state=params['random_state'],
                ccp_alpha=params['ccp_alpha']
                )
            
            # save as dict, key = tree id
            #candidates[i] = (tree, feature_subset)  
            candidates[i] = {
                'tree_object' : tree,
                'feature_subset' : feature_subset,
                'feature_subset_mapped' : feature_subset_mapped
            }
            self._status['number_of_samples_trained'] = i + 1  # keep update current status
        
        self._status['code'] = 0
        self._status['msg'] = 'TRAIN COMPLETED'
        self._candidates = candidates

    def trees_info(self):
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
                'number_of_nodes': tree.tree_number_of_nodes(),
                'number_of_leaves': tree.tree_number_of_leaves(),
                'number_of_used_attributes': len(t['feature_subset']),
                'depth': tree.tree_depth(),
                'avg_significant_digits': 0,    # Nimesh TODO: put the corresponding number here
                'hierarchy_data': tree.generate_hierarchy(),
                'confusion_matrix': tree.confusion_matrix()
            }
            candidate_info.append(tree_info)

        pareto_front = paretoAnalysis(candidate_info)
        pareto_front.pareto_analysis()

        output = {
            'total_candidates_before_pruning': len(candidate_info),
            'total_candidates_after_pruning': len([info for info in candidate_info if info['number_of_nodes'] > 1]),    # TODO: correct the pruning logic
            'pareto_front': pareto_front.pareto_front,
            'candidates': candidate_info
        }
        return output


    def tree_structure(self, tree_id: int) -> dict:
        '''
        Return the structure of the decision tree with the given id
        
        @param tree_id: int: the id of the decision tree
        
        @return: dict: the structure of the decision tree
        '''
        if not tree_id or tree_id not in self._candidates:
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

    def get_confusion_matrix(self, tree_id: int) -> dict:
        '''
        Return the confusion matrix for the decision tree with the given id
        
        @param tree_id: int: the id of the decision tree
        
        @return: dict: the confusion matrix of the decision tree
        '''
        if not self._candidates or tree_id not in self._candidates:
            return None
        return self._candidates[tree_id]['tree_object'].confusion_matrix()
