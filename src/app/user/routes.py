from flask import Blueprint, jsonify, request, make_response
from app.db import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/get-config', methods=['GET'])
def get_config():
    uuid4 = request.cookies.get('uuid')
    if uuid4 and uuid4 in db: # User Exists
        return jsonify({'code' : 200, 
                                  'data': db[uuid4]['userConfig'].get_config(), 
                                  'userId': uuid4, 
                                  'msg' : 'OK'
                                })
    # cannot find user
    return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)

@user_bp.route('/set-configs', methods=['POST'])
def set_configs():
    uuid4 = request.cookies.get('uuid')
    if uuid4 and uuid4 not in db: # cannot find user
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    # find user and set value
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON payload.'}), 400
    try:
        # Access user's decisionTreeConfig instance
        user_config = db[uuid4]['userConfig']

        # Set the parameters using the parsed JSON data
        user_config.set_config(**data)

        return jsonify({'code' : 200, 'userId': uuid4, 'msg' : 'USER CONFIG SET'}), 200
    except ValueError as e:
        return jsonify({'code' : 400, 'userId': uuid4, 'msg' : f'error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'code' : 500, 'userId': uuid4, 'msg' : 'An unexpected error occurred.'}), 500
