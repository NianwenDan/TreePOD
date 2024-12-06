from flask import Blueprint, jsonify, request, make_response
from app.db import db
from decisionTreeConfig import decisionTreeConfig
from decisionTreeCandidateGenerator import decisionTreeCandidateGenerator
from uciDatasetUtility import get_decision_tree_candidate_generator_params as get_uci_dataset_decision_tree_candidate_generator_params
from fraudDatasetUtility import get_decision_tree_candidate_generator_params as get_fraud_dataset_decision_tree_candidate_generator_params
import _thread

model_bp = Blueprint('model', __name__)

@model_bp.route('/train-start', methods=['GET'])
def train_start():
    uuid4 = request.cookies.get('uuid')
    if not uuid4 or uuid4 not in db: # cannot find user
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    user_config = db[uuid4]['userConfig']
    if not user_config.is_config_valid(): # user config either not set or not pass check
        return make_response(jsonify({'code' : 400, 'userId': uuid4, 'msg' : 'User Config Not Set Or Invalid'}), 400)
    
    # Set decision tree config
    db[uuid4]['decisionTreeConfig'] = decisionTreeConfig()
    decision_tree_config = db[uuid4]['decisionTreeConfig']
    decision_tree_config.set_parameters(user_config.get_config())

    # Create decision tree candidate generator based on user selected dataset
    user_selected_dataset = db[uuid4]['userConfig'].get_config()['dataset']
    print(f'train start, trained used dataset {user_selected_dataset}')
    if user_selected_dataset == 'UCI_Census_Income_1994':
        X_train, y_train, X_test, y_test, column_mapping = get_uci_dataset_decision_tree_candidate_generator_params()
    else:
        X_train, y_train, X_test, y_test, column_mapping = get_fraud_dataset_decision_tree_candidate_generator_params()

    if db[uuid4]['decisionTreeCandiateGenerator']:
        del db[uuid4]['decisionTreeCandiateGenerator']  # Manual Memory Recycle
    db[uuid4]['decisionTreeCandiateGenerator'] = decisionTreeCandidateGenerator(
        X_train=X_train, 
        y_train=y_train, 
        X_test=X_test, 
        y_test=y_test, 
        column_mapping=column_mapping, 
        config=decision_tree_config
    )
    
    _thread.start_new_thread(start_train_thread, (uuid4,)) # start a new thread to train data

    data = {
        'code' : 200,
        'userId': uuid4,
        'msg' : 'TRAINING START, USE /train-status TO CHECK CURRENT TRAINING STATUS'
    }
    return make_response(jsonify(data), data['code'])

def start_train_thread(uuid4):
    generator = db[uuid4]['decisionTreeCandiateGenerator']
    # train start
    generator.train()

@model_bp.route('/train-status', methods=['GET'])
def train_status():
    uuid4 = request.cookies.get('uuid')
    # cannot find user
    if not uuid4 or uuid4 not in db:
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    user_config = db[uuid4]['userConfig']
    # user config either not set or not pass check
    if not user_config.is_config_valid():
        return make_response(jsonify({'code' : 400, 'userId': uuid4, 'msg' : 'User Config Not Set Or Invalid'}), 400)
    generator = db[uuid4]['decisionTreeCandiateGenerator']
    # generator not created yet
    if not generator:
        data = {
            'code' : 200,
            'data': {
                'code' : -1,
                'msg' : 'NO GENERATOR / NOT TRAINED'
            },
            'userId': uuid4,
            'msg' : 'GENERATOR WILL BE CREATED WHEN /START-TRAIN CALLED'
        }
        return jsonify(data)
    data = {
        'code' : 200,
        'data': generator.status(),
        'userId': uuid4,
        'msg' : 'OK'
    }

    return jsonify(data)

@model_bp.route('/trees', methods=['GET'])
def trained_trees():
    uuid4 = request.cookies.get('uuid')
    # cannot find user
    if not uuid4 or uuid4 not in db:
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    user_config = db[uuid4]['userConfig']
    # user config either not set or not pass check
    if not user_config.is_config_valid():
        return make_response(jsonify({'code' : 400, 'userId': uuid4, 'msg' : 'User Config Not Set Or Invalid'}), 400)
    generator = db[uuid4]['decisionTreeCandiateGenerator']
    # generator not created yet
    if not generator:
        data = {
            'code' : 200,
            'data': {
                'code' : -1,
                'msg' : 'NO GENERATOR / NOT TRAINED'
            },
            'userId': uuid4,
            'msg' : 'GENERATOR WILL BE CREATED WHEN /START-TRAIN CALLED'
        }
        return jsonify(data)
    data = {
        'code' : 200,
        'data': None,
        'userId': uuid4,
        'msg' : 'OK'
    }
    # determine if return all trees or filtered trees
    filter = request.args.get('filter', type = str)
    user_config_settings = user_config.get_config()
    if filter == 'selected-features':
        data['data'] = generator.trees_info_with_filter(included_features=user_config_settings.get('included-attributes-for-filter'))
        return jsonify(data)
    
    data['data'] = generator.trees_info()
    return jsonify(data)