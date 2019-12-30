'''
BaseSpace Blueprint
'''
from flask import Blueprint, jsonify
from app import BASESPACE as Basespace

BP = Blueprint('basespace', __name__)

@BP.route("/basespace_runs")
def get_basespace_runs():
    ''' Get a list of runs from BaseSpace '''
    return jsonify(Basespace.get_runs())
