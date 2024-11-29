import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import _tree
from sklearn import tree
from sklearn import metrics
import matplotlib.pyplot as plt
import time
from io import BytesIO
from collections import Counter
import numpy as np

class decisionTreeTrainer:
    def __init__(self, tree_id, X_train, y_train, X_test, y_test, feature_subset=None):
        self._tree_id = tree_id
        self._X_train = X_train
        self._X_test = X_test
        self._y_train = y_train 
        self._y_test = y_test
        self._tree = None
        # Only use feature_subset
        if feature_subset:
            self._X_train = self._X_train[feature_subset]
            self._X_test = self._X_test[feature_subset]

        self._predict_data = None
        # TODO: remove hard-coded class_mapping
        self.class_mapping = {"Married": 0, "Never married": 1, "Divorced or Separated": 2, "Widowed": 3}



    def id(self) -> int:
        '''
        Return the id of the decision tree
        
        @return: int: the id of the decision tree
        '''
        return self._tree_id


    def train(self, criterion: str = 'entropy', max_depth: int = 3, min_samples_split: int = 5, random_state: int = 3, ccp_alpha: int = 3) -> None:
        '''
        Train the decision tree classifier
        
        @param criterion: str: the function to measure the quality of a split
        @param max_depth: int: the maximum depth of the tree
        @param min_samples_split: int: the minimum number of samples required to split an internal node
        @param random_state: int: the seed used by the random number generator
        @param ccp_alpha: int: complexity parameter used for Minimal Cost-Complexity Pruning
        
        @return: None
        '''
        # create a decision tree classifier
        self._tree = DecisionTreeClassifier(
            criterion=criterion,
            max_depth = max_depth,
            min_samples_split = min_samples_split,
            random_state = random_state,
            ccp_alpha = ccp_alpha
        )
        # train and fit decision tree classifer
        self._tree = self._tree.fit(self._X_train, self._y_train)


    def train_params(self) -> dict:
        '''
        Return the parameters of the decision tree classifier
        
        @return: dict: the parameters of the decision tree classifier
        '''
        return self._tree.get_params()


    def predict(self) -> dict:
        '''
        Return the prediction of the decision tree classifier
        
        @return: dict: the prediction of the decision tree classifier
        '''
        # train not started/finished
        if not self._tree:
            return None
        # no prediction yet, calculate one
        if not self._predict_data:
            dtree_y_pred = self._tree.predict(self._X_test)
            accuracy = metrics.accuracy_score(self._y_test, dtree_y_pred)
            precision = metrics.precision_score(self._y_test, dtree_y_pred, average='weighted', zero_division=0)
            recall = metrics.recall_score(self._y_test, dtree_y_pred, average='weighted')
            f1_score = metrics.f1_score(self._y_test, dtree_y_pred, average='weighted')
            # update predition data
            self._predict_data = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score
            }        
        return self._predict_data


    def tree_number_of_nodes(self) -> int:
        '''
        Return the number of nodes in the decision tree
        
        @return: int: the number of nodes in the decision tree
        '''
        # train not started/finished
        if not self._tree:
            return None
        return self._tree.tree_.node_count


    def tree_structure(self) -> dict:
        '''
        Return the structure of the decision tree
        
        @return: dict: the structure of the decision tree
        '''
        # train not started/finished
        if not self._tree:
            return None
        tree_ = self._tree.tree_
        feature_names = self._tree.feature_names_in_

        def dfs(node):
            if tree_.feature[node] != _tree.TREE_UNDEFINED:  # non-leaf node
                feature_name = feature_names[tree_.feature[node]]
                threshold = float(tree_.threshold[node])
            else:  # Leaf node
                feature_name = None
                threshold = None

            training_samples_reached = int(tree_.n_node_samples[node])
            testing_samples_reached = len(np.where(self._tree.decision_path(self._X_test).toarray()[:, node] == 1)[0])
            value = tree_.value[node].tolist()
            impurity = float(tree_.impurity[node])
            res = {
                "data": {
                    "feature": feature_name,
                    "threshold": threshold,
                    "training_samples_reached": training_samples_reached,
                    "testing_samples_reached": testing_samples_reached,
                    "value": value, # % of each class at this node
                    'labels': list(key for key, value in self.class_mapping.items() if value in self._tree.classes_),
                    "impurity": impurity
                },
                "left": None,
                "right": None
            }

            # Base case: if this is a leaf node
            if tree_.feature[node] == _tree.TREE_UNDEFINED:
                return res

            # Recursive case: Not a leaf node            
            res['left'] = dfs(tree_.children_left[node])
            res['right'] = dfs(tree_.children_right[node])
            return res
        
        # Start recursion from the root (node 0)
        return dfs(0)
    

    def tree_img(self, length, width, dpi) -> BytesIO:
        '''
        Return the image of the decision tree
        
        @param length: int: the length of the image
        @param width: int: the width of the image
        @param dpi: int: the dpi of the image
        
        @return: BytesIO: the image of the decision tree
        '''
        # train not started/finished
        if not self._tree:
            return None
        feature_names = self._tree.feature_names_in_

        if not length:
            length = 12
        if not width:
            width = 8
        if not dpi:
            dpi = 150

        img_io = BytesIO() # create the in-memory bytes buffer
        # plot the decision tree
        plt.figure(figsize=(length, width))
        tree.plot_tree(self._tree, filled=True, feature_names=feature_names)
        # save the plot to the in-memory buffer, not to a file
        plt.savefig(img_io, format='png', dpi=dpi)
        plt.close()  # close the plot to free memory
        # move the cursor of the BytesIO object to the start
        img_io.seek(0)
        return img_io


    def confusion_matrix(self) -> dict:
        '''
        Return the confusion matrix of the decision tree classifier
        
        @return: dict: the confusion matrix
        '''
        if not self._tree:
            return None
        y_pred = self._tree.predict(self._X_test)
        cm = metrics.confusion_matrix(self._y_test, y_pred)
        return {
            'confusion_matrix': cm.tolist(),  # Convert to list for JSON serialization if needed
            'labels': list(key for key, value in self.class_mapping.items() if value in self._tree.classes_)  # Add labels for the matrix /eg-class labels 0(first row 1st col) , 1(for second r and sec col etc)
        }

    def get_node_data(self):
        """
        Track data distribution at each leaf node.

        @return: 
        proportions: samples at each leaf node / all samples
        class_distributions: % of each class at each leaf node
        """
        # Apply the tree to the dataset
        leaf_indices = self._tree.apply(self._X_test)

        # Get proportions of samples in each leaf
        leaf_counts = Counter(leaf_indices)
        total_samples = sum(leaf_counts.values())
        proportions = [leaf_counts[leaf] / total_samples for leaf in np.unique(leaf_indices)]
        
        # Get class distributions for each leaf
        class_distributions = []
        for leaf in np.unique(leaf_indices):
            class_count = Counter(self._y_test[leaf_indices == leaf])
            total = sum(class_count.values())
            class_distributions.append({cls: class_count.get(cls, 0) / total for cls in range(self._tree.n_classes_)})
        
        return proportions, class_distributions

    def generate_hierarchy(self) -> dict:
        '''
        @return: hierarchy: a dict with proper format for d3 visualization of treemaps
        '''
        proportions, distributions = self.get_node_data()
        hierarchy = {"name": "Tree", "children": []}
        for i, (prop, dist) in enumerate(zip(proportions, distributions)):
            mapped_class_distribution = {key: round(dist[value], 2) for key, value in self.class_mapping.items() if value in dist}
            leaf = {
                "name": f"Leaf {i + 1}",
                "value": prop,
                "classDistribution": mapped_class_distribution
            }
            hierarchy["children"].append(leaf)
        return hierarchy