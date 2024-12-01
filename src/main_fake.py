from flask import Flask, request, jsonify, make_response, send_from_directory
import uuid
import json

from sklearn.model_selection import train_test_split
import pandas as pd

app = Flask(__name__, static_folder='./static')

@app.route('/')
def index():
    # Serve index.html for the root URL
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/dashboard')
def dashboard():
    # Serve dashboard.html when accessing /dashboard
    return send_from_directory(app.static_folder, 'dashboard.html')

@app.route('/get-started')
def get_started():
    return send_from_directory(app.static_folder, 'get-started.html')

@app.route('/settings')
def settings():
    return send_from_directory(app.static_folder, 'settings.html')

@app.route('/train-status')
def train_status():
    return send_from_directory(app.static_folder, 'train-status.html')

@app.route('/<path:filename>')
def serve_static_file(filename):
    # Serve any file in the static folder or its subdirectories
    return send_from_directory(app.static_folder, filename)

db = {}

def is_user_exists(request):
    uuid4 = request.cookies.get('uuid')
    if uuid4 and uuid4 in db:
        return True
    return False

def read_json_file(path):
    try:
        with open(f'../example/api/{path}', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {'code' : 500, 'msg' : 'JSON file not found'}
    except json.JSONDecodeError:
        return {'code' : 500, 'msg' : 'Error decoding JSON file!'}

@app.errorhandler(404)
def page_not_found(error):
    # return make_response(jsonify({'code' : 404, 'msg' : 'API NOT FOUND'}), 404)
    return send_from_directory(app.static_folder, '404.html')

@app.route('/api/v1/system/status', methods=['GET'])
def get_system_status():
    if not is_user_exists(request):
        response = make_response(jsonify({'code' : 200, 'userId': None, 'msg' : 'SYSTEM NORMAL'}), 200)
        response.set_cookie('uuid', '', max_age=0) # expire the cookie now
        return response
    uuid4 = request.cookies.get('uuid')
    return make_response(jsonify({'code' : 200, 'userId': uuid4, 'msg' : 'SYSTEM NORMAL'}), 200)

@app.route('/api/v1/system/set-userId', methods=['GET'])
def set_userId():
    # Set a cookie in the response object
    uuid4 = str(uuid.uuid4())
    # Generate decision tree candidates for current new user
    db[uuid4] = {'id' : uuid4}
    response = make_response(jsonify({'code' : 200, 'userId': uuid4, 'msg' : 'NEW USER CREATED'}), 200) # create a response object
    response.set_cookie('uuid', uuid4, max_age=60*60*2)  # cookie valid for 2 hours
    return response

@app.route('/api/v1/system/get-userId', methods=['GET'])
def get_userId():
    if is_user_exists(request):
        return make_response(jsonify({'code' : 200, 'userId': request.cookies.get('uuid'), 'msg' : 'OK'}), 200)
    else:
        response = make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND'}), 404)
        response.set_cookie('uuid', '', max_age=0) # expire the cookie now
        return response
    
@app.route('/api/v1/dataset/list', methods=['GET'])
def get_dataset_list():
    return make_response(jsonify({'code' : 200, 'msg' : 'OK', 'data': ['UCI Census Income 1994', 'Online Payment Fraud']}), 200)

@app.route('/api/v1/model/train-status', methods=['GET'])
def get_model_status():
    if not is_user_exists(request):
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    data = read_json_file('model/train-status.json')
    return make_response(jsonify(data), data['code'])

@app.route('/api/v1/model/train-start', methods=['GET'])
def get_model_train():
    if not is_user_exists(request):
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    data = read_json_file('model/train-start.json')
    return make_response(jsonify(data), data['code'])

@app.route('/api/v1/model/trees', methods=['GET'])
def get_candidate_trees():
    if not is_user_exists(request):
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    
    data = read_json_file('model/trees.json')
    return make_response(jsonify(data), data['code'])

@app.route('/api/v1/tree/hierarchy', methods=['GET'])
def get_tree_hierarchy():
    if not is_user_exists(request):
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    
    data = read_json_file('tree/hierarchy_data.json')
    return make_response(jsonify(data), data['code'])

@app.route('/api/v1/tree/structure', methods=['GET'])
def get_tree_structure():
    if not is_user_exists(request):
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    
    data = read_json_file('tree/structure.json')
    return make_response(jsonify(data), data['code'])

@app.route('/api/v1/tree/confusion-matrix', methods=['GET'])
def get_tree_confusion_matrix():
    if not is_user_exists(request):
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    
    data = read_json_file('tree/confusion-matrix.json')
    return make_response(jsonify(data), data['code'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)
    # app.run(host='0.0.0.0', port=5500)
    # print(users)
