from flask import Blueprint, jsonify

dataset_bp = Blueprint('dataset', __name__)

@dataset_bp.route('/list', methods=['GET'])
def list_datasets():
    return jsonify(
        {'code' : 200, 
         'msg' : 'OK', 
         'data': ['UCI Census Income 1994', 'Online Payment Fraud']
        })
