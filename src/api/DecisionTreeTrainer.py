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
    def __init__(self, dataset_path: str):
        self._status = {
            'code' : -1,
            'msg' : 'NOT TRAINED'
        }
        self._df = pd.read_csv(dataset_path)
        self._X_train = None
        self._X_test = None
        self._y_train = None
        self._y_test = None
        self._clf = None

        self._predict_data = None

    def status(self):
        # print(self.status)
        return self._status

    def train(self, target_column_name: str, test_size: float) -> None:
        # update status
        self._status['code'] = 1
        self._status['msg'] = 'TRAINING IN PROGRESS'
        try:
            # features (all coloums except target)
            X = self._df.drop(target_column_name, axis=1)
            # target coloum/variable
            y = self._df[target_column_name]
            # Split dataset into training set and test set
            self._X_train, self._X_test, self._y_train, self._y_test = train_test_split(X, y, test_size=test_size, random_state=1)
            # create a decision tree classifier
            self._clf = DecisionTreeClassifier(
                criterion='entropy', 
                random_state=100, 
                max_depth=3, 
                min_samples_split=5
            )
            # train and fit decision tree classifer
            self._clf = self._clf.fit(self._X_train, self._y_train)
        except Exception as e:
            self._status['code'] = 2
            self._status['msg'] = f'AN ERROR OCCURRED DURING THE TRAINING: {e}'
        
        # time.sleep(10000) # Async Testing
        
        self._status['code'] = 0
        self._status['msg'] = 'TRAINING COMPLETED'

    def predict(self):
        # train not started/finished
        if self._status['code'] != 0:
            return None
        # no prediction yet, calculate one
        if not self._predict_data:
            dtree_y_pred = self._clf.predict(self._X_test)
            accuracy = metrics.accuracy_score(self._y_test, dtree_y_pred)
            precision = metrics.precision_score(self._y_test, dtree_y_pred, average='weighted')
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

    def tree_structure(self):
        # train not started/finished
        if self._status['code'] != 0:
            return None
        tree_ = self._clf.tree_
        feature_names = self._clf.feature_names_in_

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
        if self._status['code'] != 0:
            return None
        feature_names = self._clf.feature_names_in_
        if not length:
            length = 12
        if not width:
            width = 8
        if not dpi:
            dpi = 150

        img_io = BytesIO() # create the in-memory bytes buffer
        # plot the decision tree
        plt.figure(figsize=(length, width))
        tree.plot_tree(self._clf, filled=True, feature_names=feature_names)
        # save the plot to the in-memory buffer, not to a file
        plt.savefig(img_io, format='png', dpi=dpi)
        plt.close()  # close the plot to free memory
        # move the cursor of the BytesIO object to the start
        img_io.seek(0)
        return img_io

