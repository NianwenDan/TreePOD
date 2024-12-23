from flask import Blueprint, jsonify, request, make_response
from app.db import db

tree_bp = Blueprint('tree', __name__)

@tree_bp.route('/structure', methods=['GET'])
def structure():
    uuid4 = request.cookies.get('uuid')
    # cannot find user
    if uuid4 and uuid4 not in db:
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    user_config = db[uuid4]['userConfig']
    # user config either not set or not pass check
    if not user_config.is_config_valid():
        return make_response(jsonify({'code' : 400, 'userId': uuid4, 'msg' : 'USER CONFIG NOT SET OR INVALID'}), 400)
    
    # require tree id
    tree_id = request.args.get('treeId', type = int)

    if not tree_id:
        data['code'] = 403
        data['msg'] = 'MISSING TREE ID'
        return make_response(jsonify({'code' : 400, 'userId': uuid4, 'msg' : 'MISSING TREE ID'}), 400)

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
        'data': generator.tree_structure(tree_id=tree_id),
        'userId': uuid4,
        'msg' : 'OK'
    }

    return jsonify(data)

@tree_bp.route('/hierarchy', methods=['GET'])
def hierarchy():
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
        'data': generator.get_pareto_hierarchy_data(),
        'userId': uuid4,
        'msg' : 'OK'
    }

    return jsonify(data)

@tree_bp.route('/confusion-matrix', methods=['GET'])
def confusion_matrix():
    uuid4 = request.cookies.get('uuid')
    # cannot find user
    if uuid4 and uuid4 not in db:
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    user_config = db[uuid4]['userConfig']
    # user config either not set or not pass check
    if not user_config.is_config_valid():
        return make_response(jsonify({'code' : 400, 'userId': uuid4, 'msg' : 'USER CONFIG NOT SET OR INVALID'}), 400)
    
    # require tree id
    tree_id = request.args.get('treeId', type = int)

    if not tree_id:
        data['code'] = 403
        data['msg'] = 'MISSING TREE ID'
        return make_response(jsonify({'code' : 400, 'userId': uuid4, 'msg' : 'MISSING TREE ID'}), 400)

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
        'data': generator.get_confusion_matrix(tree_id=tree_id),
        'userId': uuid4,
        'msg' : 'OK'
    }

    return jsonify(data)
