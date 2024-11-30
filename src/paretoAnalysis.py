import numpy as np

class paretoAnalysis:
    def __init__(self, candidates): #, maximize_attributes=None):
        self.candidates = candidates
        self.pareto_front = {}
        # TODO: remove hard-coded part
        self.attributes = ["depth", "f1_score", "number_of_nodes", "number_of_leaves", "number_of_used_attributes"]
        self.attribute_pairs = [(a, b) for a in self.attributes for b in self.attributes if a!= b]
        #self.maximize_attributes = set(maximize_attributes) if maximize_attributes else set()
        self.maximize_attributes = set({"f1_score"})

    def find_pareto_optimal(self, attribute1, attribute2):
        """
        Finds Pareto-optimal tree IDs based on two attributes.
        If an attribute is in `self.max_list`, it will be maximized.
        
        Args:
            attribute1: First attribute to optimize.
            attribute2: Second attribute to optimize.

        Returns:
            List of Pareto-optimal tree IDs.
        """
        # Extract the two attributes and tree IDs
        '''
        data_points = np.array([
            [
                round(-candidate['predicted'][attribute1],3) if attribute1 in self.maximize_attributes else candidate['predicted'][attribute1],
                round(-candidate['predicted'][attribute2],3) if attribute2 in self.maximize_attributes else candidate['predicted'][attribute2],
                candidate['tree_id']
            ] 
            for candidate in self.candidates
        ])'''

        data_points = np.array([
            [
                round(-candidate.get(attribute1, candidate['predicted'].get(attribute1, 0)), 3) if attribute1 in self.maximize_attributes else candidate.get(attribute1, candidate['predicted'].get(attribute1, 0)),
                round(-candidate.get(attribute2, candidate['predicted'].get(attribute2, 0)), 3) if attribute2 in self.maximize_attributes else candidate.get(attribute2, candidate['predicted'].get(attribute2, 0)),
                candidate['tree_id']
            ]
            for candidate in self.candidates
        ])
        
        # Prepare the Pareto front
        pareto_front = []
        seen = set()
        for point in data_points:
            # Check if the point is dominated
            is_dominated = False
            for other_point in data_points:
                if (
                    (other_point[0] <= point[0] and other_point[1] <= point[1])  # Other point is better or equal in all dimensions
                    and (other_point[0] < point[0] or other_point[1] < point[1])  # Strictly better in at least one dimension
                ):
                    is_dominated = True
                    break
            if not is_dominated:
                if (point[0], point[1]) not in seen:
                    seen.add((point[0], point[1]))
                    pareto_front.append(point)
        print ('pareto_front: ', pareto_front)
        # Extract the Pareto-optimal tree IDs
        pareto_optimal_ids = [int(p[2]) for p in pareto_front]
        return pareto_optimal_ids



    def pareto_analysis(self):
        normalized_pairs = set(tuple(sorted(pair)) for pair in self.attribute_pairs)

        for attribute1, attribute2 in normalized_pairs:
            key = f"{attribute1}_{attribute2}"

            if key not in self.pareto_front:
                self.pareto_front[key] = self.find_pareto_optimal(attribute1, attribute2)
