from flask import Flask, request, jsonify, make_response, abort, redirect, render_template_string
from decisionTree import decisionTree
import threading
import uuid

app = Flask(__name__)

# @app.route('/')
# def index():
#     return redirect("https://google.com")

# dt = decisionTree(dataset_path='./diabetes.csv')
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
    db[uuid4] = {'id' : uuid4,
                 'model' : decisionTree(dataset_path='./diabetes.csv')
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
    threading.Thread(model.train(target_column_name='Outcome', test_size=0.2)).start()
    data = {
        'code' : 200,
        'userId': request.cookies.get('uuid'),
        'msg' : 'TRAINING START, USE /train-status TO CHECK CURRENT TRAINING STATUS'
    }
    return make_response(jsonify(data), data['code'])

@app.route('/api/v1/model/predict', methods=['GET'])
def get_model_predict():
    if not is_user_exists(request):
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    model = get_user_model(request)
    predict = model.predict()
    data = {
        'code' : 200,
        'userId': request.cookies.get('uuid'),
        'msg' : 'OK',
        'data': predict
    }
    if not predict:
        data['code'] = 404
        data['msg'] = 'TRAINING PROCEDURE NOT STARTED OR INCOMPLETE, USE /train-status TO CHECK CURRENT TRAINING STATUS'
    return make_response(jsonify(data), data['code'])

@app.route('/api/v1/tree/structure', methods=['GET'])
def get_tree_structure():
    if not is_user_exists(request):
        return make_response(jsonify({'code' : 404, 'userId': None, 'msg' : 'NO USER FOUND, CREATE A USER FIRST'}), 404)
    model = get_user_model(request)
    data = {
        'code' : 200,
        'userId': request.cookies.get('uuid'),
        'msg' : 'OK',
        'data': model.tree_structure()
    }
    return make_response(jsonify(data), data['code'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)
    # app.run(host='0.0.0.0', port=5500)
    # print(users)
