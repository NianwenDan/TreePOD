import random
import numpy as np
import pandas as pd
import json
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
# from scipy.spatial import ConvexHull
from collections import Counter
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from itertools import chain

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
            X_train_subset = self.X_train[self.feature_subset]
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
    def __init__(self, X_train, y_train, column_mapping, config=None):
        self.X_train = X_train
        self.y_train = y_train
        self.column_mapping = column_mapping
        self.config = config if config is not None else DecisionTreeConfig()
        self.num_candidates = self.config.total_samples



    def generate_tree(self):
        candidates = []
        total_features = len(self.column_mapping)
        for _ in range(self.num_candidates):
            params = self.config.sample_parameters(total_features)
            feature_subset_index = self.sample_feature_subset(params['nr_of_nodes'])
            feature_subset = [list(self.column_mapping.keys())[i] for i in feature_subset_index]
            feature_subset_mapped = []
            for i in feature_subset:
                feature_subset_mapped += self.column_mapping[i]
            trainer = DecisionTreeTrainer(self.X_train, self.y_train, feature_subset_mapped)
            tree = trainer.train_tree(params)
            candidates.append((tree, feature_subset, feature_subset_mapped))
        return candidates

    def sample_feature_subset(self, subset_size):
        total_features = len(self.column_mapping)
        return random.sample(range(total_features), subset_size)

class ParetoAnalysis:
    def __init__(self, candidates, maximize_attributes=None):
        self.candidates = candidates
        self.maximize_attributes = set(maximize_attributes) if maximize_attributes else set()
        self.pareto_front = {}

    def find_pareto_optimal(self, attribute1, attribute2):
        # Extract the two attributes from each candidate to create a 2D dataset
        data_points = np.array([[candidate[attribute2], candidate[attribute1], candidate['tree_id']] for candidate in self.candidates])
        # Check if attribute needs maximization and invert it if needed
        '''if attribute1 in self.maximize_attributes:
            data_points[:, 0] = -data_points[:, 0]
        if attribute2 in self.maximize_attributes:
            data_points[:, 1] = -data_points[:, 1]
        '''
        # Compute convex hull to find Pareto-optimal points
        #hull = ConvexHull(data_points)
        #pareto_indices = hull.vertices

        # implementation 2
        pareto_front = []
        max_y = -np.inf
        # minimize both attributes
        #data_points = data_points[np.lexsort((data_points[:, 1], data_points[:, 0]))]
        data_points = data_points[np.lexsort((data_points[:, 1], data_points[:, 0]))]
        print ('data points: ', data_points)
        for data_point in data_points:
            if data_point[1] > max_y:
                pareto_front.append(data_point)
                max_y = data_point[1]
        print ('pareto_front: ', pareto_front)

        # Return Pareto-optimal tree IDs
        #pareto_optimal_ids = [self.candidates[i]['tree_id'] for i in pareto_indices]
        pareto_optimal_ids = [int(i[2]) for i in pareto_front]
        return pareto_optimal_ids

    def pareto_analysis(self, attribute_pairs):
        normalized_pairs = set(tuple(sorted(pair)) for pair in attribute_pairs)

        for attribute1, attribute2 in normalized_pairs:
            key = f"{attribute1}_{attribute2}"

            if key not in self.pareto_front:
                self.pareto_front[key] = self.find_pareto_optimal(attribute1, attribute2)

class DecisionTreeOutput:
    def __init__(self, candidates, X_test, y_test):
        self.candidates = candidates
        self.X_test = X_test
        self.y_test = y_test
        self.pareto_front = None
        self.X_test_subset = None
        self.class_mapping = {"Married": 0, "Never married": 1, "Divorced or Separated": 2, "Widowed": 3}

    def generate_output(self):
        candidate_info = []
        for idx, (tree, _, feature_subset_mapped) in enumerate(self.candidates):
            if feature_subset_mapped:
                self.X_test_subset = self.X_test[feature_subset_mapped]
            else:
                self.X_test_subset = self.X_test
            y_pred = tree.predict(self.X_test_subset)        
            f1 = f1_score(self.y_test, y_pred, average='weighted')


            # From Nianwen: Step 7: Track data flow through the tree (as in the previous implementation)
            def get_node_data(self, tree):
                """
                Track data distribution at each tree node.

                Parameters:
                - tree: Trained decision tree.
                - X: Input features.
                - original_df: Original dataframe (for categorical values).
                - categorical_columns: List of categorical column names from original_df.

                Returns:
                - node_data: Dictionary with data distributions for each node.
                """
                # Apply the tree to the dataset
                leaf_indices = tree.apply(self.X_test_subset)

                #leaf_classes = [np.argmax(Counter(self.y_test[leaf_indices == leaf]).values()) for leaf in np.unique(leaf_indices)]
                    
                # Get proportions of samples in each leaf
                leaf_counts = Counter(leaf_indices)
                total_samples = sum(leaf_counts.values())
                proportions = [leaf_counts[leaf] / total_samples for leaf in np.unique(leaf_indices)]
                
                # Get class distributions for each leaf
                class_distributions = []
                for leaf in np.unique(leaf_indices):
                    class_count = Counter(self.y_test[leaf_indices == leaf])
                    total = sum(class_count.values())
                    class_distributions.append({cls: class_count.get(cls, 0) / total for cls in range(tree.n_classes_)})
                
                return proportions, class_distributions

            def generate_hierarchy(self, proportions, distributions):
                hierarchy = {"name": "Tree", "children": []}
                for i, (prop, dist) in enumerate(zip(proportions, distributions)):
                    mapped_class_distribution = {key: round(dist[value], 2) for key, value in self.class_mapping.items() if value in dist}
                    leaf = {
                        "name": f"Leaf {i + 1}",
                        "value": prop * 100,  # Scale proportion to a meaningful value
                        "classDistribution": mapped_class_distribution
                    }
                    hierarchy["children"].append(leaf)
                return hierarchy


                '''
                # Get the tree structure
                tree_ = tree.tree_
                n_nodes = tree_.node_count

                # Prepare a dictionary to store data at each node
                node_data = {i: {'total_count': 0, 'categorical_distribution': {col: {} for col in self.categorical_columns}} for i in range(n_nodes)}
                print ('node_data: ', node_indices)
                
                # Iterate over each data point
                for i, node_index in enumerate(node_indices):
                    node_data[node_index]['total_count'] += 1

                    # Update categorical distribution using the original DataFrame
                    for col in self.categorical_columns:
                        value = original_df.iloc[i][col]
                        if value not in node_data[node_index]['categorical_distribution'][col]:
                            node_data[node_index]['categorical_distribution'][col][value] = 0
                        node_data[node_index]['categorical_distribution'][col][value] += 1

                return node_data    '''

            proportions, distributions = get_node_data(self, tree)
            hierarchy_data = generate_hierarchy(self, proportions, distributions)

            candidate_info.append({
                'tree_id': idx + 1,
                'params': tree.get_params(),
                'hierarchy_data': hierarchy_data,
                'Nr. of Nodes': tree.tree_.node_count,
                'Accuracy [F1 score]': round(f1, 8)
            })
            

        # All possible x, y attribute pairs
        attribute_pairs = [
            #("depth", "f1_score"),
            ("Nr. of Nodes", "Accuracy [F1 score]"),
            ("Accuracy [F1 score]", "Nr. of Nodes")
        ]
        # Other attributes not in this set would be minimized when finding pareto front
        maximize_attributes = {"Accuracy [F1 score]"}
        pareto_front = ParetoAnalysis(candidate_info, maximize_attributes)
        pareto_front.pareto_analysis(attribute_pairs)
        self.pareto_front = pareto_front.pareto_front

        
        output = {
            'total_candidates_before_pruning': len(self.candidates),
            'total_candidates_after_pruning': len([tree for (tree, _, _) in self.candidates if tree.tree_.node_count > 1]),
            'pareto_front': self.pareto_front,
            'candidates': candidate_info
        }

        with open('trees.3.json', 'w') as json_file:
            json.dump(output, json_file, indent=4)
    """
    def group_candidates_by_nodes(self, candidate_info):
        grouped = {}
        for candidate in candidate_info:
            num_nodes = candidate['Nr. of Nodes']
            if num_nodes not in grouped:
                grouped[num_nodes] = []
            grouped[num_nodes].append(candidate)
        return grouped
    """

# Main
if __name__ == "__main__":
    # Data loading
    '''
    df = pd.read_csv('diabetes.csv')
    X = df.drop('Outcome', axis=1).values
    y = df['Outcome'].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=100)
    '''
    df = pd.read_csv('datasets/uci_adult.data.csv').drop('relationship', axis=1)
    # Step 2: Clean categorical data
    categorical_columns = [
        'workclass', 'education', 'occupation',
        'race', 'sex', 'native-country', 'income'
    ]
    
    for col in categorical_columns:
        df[col] = df[col].str.strip()

    # Step 3: Handle missing values
    # For numeric columns, fill missing values with the median
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())

    # For categorical columns, fill missing values with the mode (most frequent value)
    for col in categorical_columns:
        df[col] = df[col].fillna(df[col].mode()[0])

    # Step 5: Split categorical and numerical columns
    # Apply one-hot encoding to categorical columns
    categorical_df = pd.get_dummies(df[[col for col in categorical_columns if col != 'marital-status']])  # Exclude the target column

    # Combine numerical and encoded categorical data
    X = pd.concat([df[numeric_columns], categorical_df], axis=1) 

    # Step 4: Encode the target variable   
    y = df['marital-status'].map({' Never-married': 1, ' Married-civ-spouse': 0, ' Married-spouse-absent': 0, ' Married-AF-spouse': 0, ' Divorced': 2, ' Separated': 2, ' Widowed': 3})
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=100)
    column_mapping = {original: [col for col in X_train.columns if col.startswith(original)]
            for original in categorical_columns}
    for key in numeric_columns:
        column_mapping[key] = [] + [key]

    # User-defined config
    user_config = DecisionTreeConfig(max_depth_range=range(1, 7), random_state_range=range(50, 51), total_samples=1000)

    # Generate decision tree candidates
    generator = DecisionTreeCandidateGenerator(X_train, y_train, column_mapping, config=user_config)
    candidates = generator.generate_tree()

    # Output to json. Vis will load json data
    output = DecisionTreeOutput(candidates, X_test, y_test)
    output.generate_output()