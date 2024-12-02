
class userConfig:
    def __init__(self):
        self._feature_set = None
        self._selection_criterion = None # This should be an array list all possible criterions
        self._max_depth_range = None # This should be an array [0, 100]
        self._min_leaf_size = None
        self._is_enable_puring = None
        self._round_to_significant_digit = None
        self._stochastic_samples = None

    def set_config(self, **kwargs):
        name_mapping = {
            'feature-set': '_feature_set',
            'selection-criterion': '_selection_criterion',
            'max-depth-range': '_max_depth_range',
            'min-leaf-size': '_min_leaf_size',
            'pruning': '_is_enable_puring',
            'round-to-significant-digit' : '_round_to_significant_digit',
            'stochastic-samples' : '_stochastic_samples'
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
            
    def get_config(self):
        return {
            'feature-set': self._feature_set,
            'selection-criterion': self._selection_criterion,
            'max-depth-range': self._max_depth_range,
            'min-leaf-size': self._min_leaf_size,
            'pruning': self._is_enable_puring,
            'round-to-significant-digit' : self._round_to_significant_digit,
            'stochastic-samples' : self._stochastic_samples
        }
    
        # Example User Config
        # {
        #     "feature-set": ['1', '2', '3'],
        #     "max-depth-range": [0, 100],
        #     "min-leaf-size": 20,
        #     "pruning": True,
        #     "round-to-significant-digit": 3,
        #     "selection-criterion": ['gini', 'entropy', 'log_loss'],
        #     "stochastic-samples": 321
        # }