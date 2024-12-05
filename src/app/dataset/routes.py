from flask import Blueprint, jsonify, request, make_response
from uciDatasetUtility import features_in_dataset as features_in_UCI_dataset

dataset_bp = Blueprint('dataset', __name__)

@dataset_bp.route('/list', methods=['GET'])
def list_datasets():
    return jsonify(
        {'code' : 200, 
         'msg' : 'OK', 
         'data': ['UCI Census Income 1994', 'Online Payment Fraud']
        })

@dataset_bp.route('/attributes', methods=['GET'])
def list_attributes():
    dataset = request.args.get('dataset', type = str)
    if dataset == 'UCI_Census_Income_1994':
        return jsonify(
        {'code' : 200, 
         'msg' : 'OK', 
         'data': ['capital-loss', 'income']
        })
    elif dataset == 'Online_Payment_Fraud':
        return jsonify(
        {'code' : 200, 
         'msg' : 'OK', 
         'data': [] # To be Implemened
        })
    return make_response(jsonify({'code' : 404, 'msg' : 'NO DATASET PASSED IN OR DATASET CANNOT FOUND'}), 404)