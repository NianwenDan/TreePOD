from flask import Blueprint, jsonify, request, make_response
from app.db import db
import uuid
from userConfig import userConfig

system_bp = Blueprint('system', __name__)

@system_bp.route('/status', methods=['GET'])
def status():
    uuid4 = request.cookies.get('uuid')
    if uuid4 and uuid4 in db: # User Exists
        return jsonify({'code' : 200, 'userId': uuid4, 'msg' : 'SYSTEM NORMAL'})
    response = make_response(jsonify({'code' : 200, 'userId': None, 'msg' : 'SYSTEM NORMAL'}), 200)
    response.set_cookie('uuid', '', max_age=0) # expire the cookie now
    return response

@system_bp.route('/set-userId', methods=['GET'])
def set_user_id():
    # Set a cookie in the response object
    uuid4 = str(uuid.uuid4())
    # Generate decision tree candidates for current new user
    db[uuid4] = {'id' : uuid4,
                 'userConfig' : userConfig(),
                 'decisionTreeConfig' : None,
                 'decisionTreeCandiateGenerator' : None
                }
    response = make_response(jsonify({'code' : 200, 'userId': uuid4, 'msg' : 'NEW USER CREATED'}), 200) # create a response object
    response.set_cookie('uuid', uuid4, max_age=60*60*2)  # cookie valid for 2 hours
    return response

@system_bp.route('/get-userId', methods=['GET'])
def get_user_id():
    uuid4 = request.cookies.get('uuid')
    if uuid4 and uuid4 in db: # User Exists
        return make_response(jsonify({'code' : 200, 'userId': request.cookies.get('uuid'), 'msg' : 'OK'}), 200)
    else:
        response = make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND'}), 404)
        response.set_cookie('uuid', '', max_age=0) # expire the cookie now
        return response