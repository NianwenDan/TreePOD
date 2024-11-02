from flask import Flask, request, jsonify, make_response, send_file
from decisionTreeCandidateGenerator import decisionTreeCandidateGenerator
from decisionTreeConfig import decisionTreeConfig
import threading
import uuid
from functools import wraps
from config import SECRET_TOKEN

from sklearn.model_selection import train_test_split
import pandas as pd

app = Flask(__name__)

# @app.route('/')
# def index():
#     return redirect("https://google.com")

db = {}

def is_user_exists(request):
    uuid4 = request.cookies.get('uuid')
    if uuid4 and uuid4 in db:
        return True
    return False

def get_user_model(request):
    uuid4 = request.cookies.get('uuid')
    return db[uuid4]['model']

@app.errorhandler(404)
def page_not_found(error):
    return make_response(jsonify({'code' : 404, 'msg' : 'API NOT FOUND'}), 404)

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
    # TODO: Load Data Here to Train Data For Now, Find a Way So User Can Upload Dataset
    df = pd.read_csv('diabetes.csv')
    # X = df.drop('Outcome', axis=1).values
    # y = df['Outcome'].values
    X = df.drop('Outcome', axis=1)
    y = df['Outcome']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)
    # User-defined config
    user_config = decisionTreeConfig(max_depth_range=range(1, 7), random_state_range=range(50, 51), total_samples=300)
    # Generate decision tree candidates for current new user
    db[uuid4] = {'id' : uuid4,
                 'model' : decisionTreeCandidateGenerator(X_train, y_train, X_test, y_test, config=user_config)
                }
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

@app.route('/api/v1/model/train-status', methods=['GET'])
def get_model_status():
    if not is_user_exists(request):
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    model = get_user_model(request)
    data = {
        'code' : 200,
        'userId': request.cookies.get('uuid'),
        'msg' : 'OK',
        'data': model.status()
    }
    return make_response(jsonify(data), data['code'])

@app.route('/api/v1/model/train-start', methods=['GET'])
def get_model_train():
    if not is_user_exists(request):
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    model = get_user_model(request)
    # Start the training in a separate thread
    threading.Thread(model.train()).start()
    data = {
        'code' : 200,
        'userId': request.cookies.get('uuid'),
        'msg' : 'TRAINING START, USE /train-status TO CHECK CURRENT TRAINING STATUS'
    }
    return make_response(jsonify(data), data['code'])

# @app.route('/api/v1/model/predict', methods=['GET'])
# def get_model_predict():
#     if not is_user_exists(request):
#         return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
#     model = get_user_model(request)
#     predict = model.predict()
#     data = {
#         'code' : 200,
#         'userId': request.cookies.get('uuid'),
#         'msg' : 'OK',
#         'data': predict
#     }
#     if not predict:
#         data['code'] = 404
#         data['msg'] = 'TRAINING PROCEDURE NOT STARTED OR INCOMPLETE, USE /train-status TO CHECK CURRENT TRAINING STATUS'
#     return make_response(jsonify(data), data['code'])

@app.route('/api/v1/model/trees', methods=['GET'])
def get_candidate_trees():
    if not is_user_exists(request):
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    
    is_grouped_by_nodes = request.args.get('isGrouped', type = bool)
    model = get_user_model(request)
    trees_info = model.trees_info(is_grouped_by_nodes=is_grouped_by_nodes)
    data = {
        'code': trees_info[0] if trees_info[0] != 200 else 200,
        'userId': request.cookies.get('uuid'),
        'msg': trees_info[1] if trees_info[0] != 200 else 'OK',
        'data': None if trees_info[0] != 200 else trees_info[1]
    }
    return make_response(jsonify(data), data['code'])

@app.route('/api/v1/tree/structure', methods=['GET'])
def get_tree_structure():
    if not is_user_exists(request):
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    
    tree_id = request.args.get('treeId', type = int)
    model = get_user_model(request)
    trees_structure = model.tree_structure(tree_id=tree_id)
    data = {
        'code': trees_structure[0] if trees_structure[0] != 200 else 200,
        'userId': request.cookies.get('uuid'),
        'msg': trees_structure[1] if trees_structure[0] != 200 else 'OK',
        'data': None if trees_structure[0] != 200 else trees_structure[1]
    }
    return make_response(jsonify(data), data['code'])

@app.route('/api/v1/tree/image', methods=['GET'])
def get_tree_image():
    if not is_user_exists(request):
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    
    tree_id = request.args.get('treeId', type = int)
    length = request.args.get('length', type = int)
    width = request.args.get('width', type = int)
    dpi = request.args.get('dpi', type = int)
    model = get_user_model(request)
    img = model.tree_image(tree_id, length, width, dpi)

    if not tree_id:
        data = {
            'code': 403,
            'userId': request.cookies.get('uuid'),
            'msg': 'TREE ID REQURIED',
            'data': None
        }
        return make_response(jsonify(data), data['code'])
    return send_file(img, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)
    # app.run(host='0.0.0.0', port=5500)
    # print(users)
