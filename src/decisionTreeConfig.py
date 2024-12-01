import random
import numpy as np

class decisionTreeConfig:
    def __init__(self):
        self._criterion_options = None
        self._max_depth_range = None
        self._min_samples_split_range = None
        self._random_state_range = None
        self._ccp_alpha_range = None
        self._total_samples = None


    def _generate_random_int(self, min, max):
        return random.choice(range(min, max))


    def set_parameters(self, **kwargs):
        """
        Allows the user to update the existing parameter ranges and options.
        Parameters can be set by specifying them as keyword arguments.
        """
        # Outside Name Mappomh
        name_mapping = {
            'criterion': '_criterion_options',
            'max_depth': '_max_depth_range',
            'min_samples_split': '_min_samples_split_range',
            'random_state': '_random_state_range',
            'ccp_alpha': '_ccp_alpha_range',
            'total_samples' : '_total_samples'
        }
        for key, value in kwargs.items():
            print(key, value)
            internel_key = name_mapping.get(key) # This is the internel class attribute name
            if not internel_key:
                raise ValueError(f"'{key}' is not a valid parameter name.")
            if hasattr(self, internel_key):
                setattr(self, internel_key, value)
            else:
                raise ValueError(f"'{key}' is not a valid parameter name.")
            
    def pick_random_parameters(self):
        '''
        Set Random Parameters
        '''
        possible_criterion_options = ['gini', 'entropy', 'log_loss']
        possible_ccp_alpha_range = np.linspace(0.0, 0.05, 10)
        return {
            'criterion': possible_criterion_options[self._generate_random_int(0, 3)],
            'max_depth': self._generate_random_int(1, 11),
            'min_samples_split': self._generate_random_int(2, 11),
            'random_state': self._generate_random_int(0, 100),
            'ccp_alpha': random.choice(possible_ccp_alpha_range),
            'total_samples' : self._generate_random_int(100, 1000)
        }
    
    def fill_undefined_parameters_randomly(self):
        data = self.pick_random_parameters()
        if not self._criterion_options:
            self._criterion_options = data['criterion']
        if not self._max_depth_range:
            self._max_depth_range = data['max_depth']
        if not self._min_samples_split_range:
            self._min_samples_split_range = data['min_samples_split']
        if not self._random_state_range:
            self._random_state_range = data['random_state']
        if not self._ccp_alpha_range:
            self._ccp_alpha_range = data['ccp_alpha']
        if not self._total_samples:
            self._total_samples = data['total_samples']


    def get_all_parameter(self, total_features=None):
        """
        Retrieves the stored parameters
        """
        return {
            'criterion': self._criterion_options,
            'max_depth': self._max_depth_range,
            'min_samples_split': self._min_samples_split_range,
            'random_state': self._random_state_range,
            'nr_of_attributes': total_features, # This is randomly generated each time
            'ccp_alpha': self._ccp_alpha_range,
            'total_samples' : self._total_samples
        }

    # def sample_parameters(self, total_features):
    #     criterion = random.choice(self._criterion_options)
    #     max_depth = random.choice(self._max_depth_range)
    #     min_samples_split = random.choice(self._min_samples_split_range)
    #     random_state = random.choice(self._random_state_range)
    #     nr_of_attributes = random.randint(1, total_features)
    #     ccp_alpha = random.choice(self._ccp_alpha_range)
    #     return {
    #         'criterion': criterion,
    #         'max_depth': max_depth,
    #         'min_samples_split': min_samples_split,
    #         'random_state': random_state,
    #         'nr_of_attributes': nr_of_attributes,
    #         'ccp_alpha': ccp_alpha, # TODO: add another input to activate/deactivate pruning
    #         'total_samples' : self._total_samples
    #     }