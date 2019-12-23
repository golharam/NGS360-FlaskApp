'''
Main application endpoints
'''
from flask import Blueprint, current_app

BP = Blueprint('main', __name__)

@BP.route('/')
def index():
    '''
    Home Page URL: /
    '''
    html = "<h3>Hello!</h3>" \
            "<b>Testing:</b> {testing}<br/>" \
            "<b>Debug:</b> {debug}<br/>"
    return html.format(testing=current_app.config['TESTING'],
                       debug=current_app.config['DEBUG'])
