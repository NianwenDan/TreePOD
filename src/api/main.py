from flask import Flask, request, jsonify, make_response, abort, redirect, render_template_string
from decisionTree import decisionTree
import threading
import uuid

app = Flask(__name__)

# @app.route('/')
# def index():
#     return redirect("https://google.com")

dt = decisionTree(dataset_path='./diabetes.csv')
cookie = {}

@app.errorhandler(404)
def page_not_found(error):
    return make_response(jsonify({'code' : 404, 'msg' : 'API NOT FOUND'}), 404)

@app.route('/api/v1/system/status', methods=['GET'])
def get_system_status():
    return make_response(jsonify({'code' : 200, 'msg' : 'SYSTEM NORMAL'}), 200)

@app.route('/api/v1/system/set-cookie', methods=['GET'])
def set_cookie():
    response = make_response("Cookie has been set!") # Create a response object
    # Set a cookie in the response object
    uuid4 = str(uuid.uuid4())
    cookie[uuid4] = {'id' : uuid4,
                     'dt' : decisionTree(dataset_path='./diabetes.csv')
                     }
    response.set_cookie('uuid', uuid4, max_age=60*60*24)  # Cookie valid for 1 day
    return response

@app.route('/api/v1/system/get-cookie', methods=['GET'])
def get_cookie():
    uuid4 = request.cookies.get('uuid')
    if uuid4 in cookie:
        return make_response(jsonify(cookie[uuid4]['id']), 200)
    else:
        return 'No cookie found!'

@app.route('/api/v1/template/tree/train-status', methods=['GET'])
def get_template_tree_status():
    return make_response(jsonify(dt.status()), 200)

@app.route('/api/v1/template/tree/train-start', methods=['GET'])
def get_template_tree_train():
    # Start the training in a separate thread
    threading.Thread(dt.train(target_column_name='Outcome', test_size=0.2)).start()
    # dt.train(target_column_name='Outcome', test_size=0.2)
    return make_response(jsonify({'code' : 200, 'msg' : 'TRAINING START'}), 200)

@app.route('/api/v1/template/tree/predict', methods=['GET'])
def get_template_tree_predict():
    return make_response(jsonify(dt.predict()), 200)

@app.route('/api/v1/template/tree/datastructure', methods=['GET'])
def get_template_tree_datastructure():
    return make_response(jsonify(dt.tree_structure()), 200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)
    # app.run(host='0.0.0.0', port=5500)
    # print(users)
