from flask import Blueprint, jsonify, request, make_response
from app.db import db
from decisionTreeConfig import decisionTreeConfig
from decisionTreeCandidateGenerator import decisionTreeCandidateGenerator
from uciDatasetUtility import get_decision_tree_candidate_generator_params
import _thread

model_bp = Blueprint('model', __name__)

@model_bp.route('/train-start', methods=['GET'])
def train_start():
    uuid4 = request.cookies.get('uuid')
    if uuid4 and uuid4 not in db: # cannot find user
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    user_config = db[uuid4]['userConfig']
    if not user_config.is_config_valid(): # user config either not set or not pass check
        return make_response(jsonify({'code' : 400, 'userId': uuid4, 'msg' : 'User Config Not Set Or Invalid'}), 400)
    
    # Set decision tree config
    db[uuid4]['decisionTreeConfig'] = decisionTreeConfig()
    decision_tree_config = db[uuid4]['decisionTreeConfig']
    decision_tree_config.set_parameters(user_config.get_config())

    # Create decision tree candidate generator
    X_train, y_train, X_test, y_test, column_mapping = get_decision_tree_candidate_generator_params()
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
    if uuid4 and uuid4 not in db:
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
    if uuid4 and uuid4 not in db:
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
        'data': generator.trees_info(),
        'userId': uuid4,
        'msg' : 'OK'
    }

    return jsonify(data)