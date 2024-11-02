import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import _tree
from sklearn import tree
from sklearn import metrics
import matplotlib.pyplot as plt
import time
from io import BytesIO

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
            self._X_train = self._X_train.iloc[:, feature_subset]
            self._X_test = self._X_test.iloc[:, feature_subset]

        self._predict_data = None

    def id(self):
        return self._tree_id

    def train(self, criterion: str = 'entropy', max_depth: int = 3, min_samples_split: int = 5, random_state: int = 3, ccp_alpha: int = 3) -> None:
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

    def train_params(self):
        return self._tree.get_params()

    def predict(self):
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

    def tree_number_of_nodes(self):
        # train not started/finished
        if not self._tree:
            return None
        return self._tree.tree_.node_count

    def tree_structure(self):
        # train not started/finished
        if not self._tree:
            return None
        tree_ = self._tree.tree_
        feature_names = self._tree.feature_names_in_
        # feature_names = getattr(self._tree, 'feature_names_in_', [f'feature_{i}' for i in range(tree_.n_features)])

        def dfs(node):
            # get necessary value
            feature_name = feature_names[tree_.feature[node]]
            threshold = float(tree_.threshold[node])
            training_samples_reached = int(tree_.n_node_samples[node])
            value = tree_.value[node].tolist()
            impurity = float(tree_.impurity[node])
            res = {
                "data": {
                    "feature": feature_name,
                    "threshold": threshold,
                    "training_samples_reached": training_samples_reached,
                    "value": value,
                    "impurity": impurity
                },
                "left": None,
                "right": None
            }
            
            # base case: If this is a leaf node
            if tree_.feature[node] == _tree.TREE_UNDEFINED:
                return res 
            # recursive case: Not a leaf node
            # create the node dictionary with feature, threshold, and recursive children
            res['left'] = dfs(tree_.children_left[node])
            res['right'] = dfs(tree_.children_right[node])
            return res
        
        # Start recursion from the root (node 0)
        return dfs(0)
    
    def tree_img(self, length, width, dpi):
        # train not started/finished
        if not self._tree:
            return None
        feature_names = self._tree.feature_names_in_
        # tree_ = self._tree.tree_
        # feature_names = getattr(self._tree, 'feature_names_in_', [f'feature_{i}' for i in range(tree_.n_features)])

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

