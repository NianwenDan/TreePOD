import random
import numpy as np

class decisionTreeConfig:
    def __init__(self):
        self._user_config = None


    def _generate_random_int(self, min, max):
        return random.choice(range(min, max))


    def set_parameters(self, user_config_json):
        self._user_config = user_config_json
            
    def _pick_random_parameters(self):
        '''
        Set Random Parameters
        '''
        possible_ccp_alpha_range = np.linspace(0.0, 0.05, 10)
        return {
            'criterion': random.choice(self._user_config['selection-criterion']),
            'max_depth': self._generate_random_int(self._user_config['max-depth-range'][0], self._user_config['max-depth-range'][1]),
            'min_samples_split': self._user_config['min-leaf-size'],
            'random_state': self._generate_random_int(0, 100),
            'ccp_alpha': random.choice(possible_ccp_alpha_range) if self._user_config['pruning'] else 0,
            'total_samples' : self._user_config['stochastic-samples']
        }


    def get_rand_param_based_on_user_config(self, total_features=None):
        """
        Retrieves the stored parameters
        """
        randData = self._pick_random_parameters()
        randData['nr_of_attributes'] = self._generate_random_int(1, total_features+1)
        return randData