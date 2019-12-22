from flask import Blueprint, current_app

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    html = "<h3>Hello!</h3>" \
            "<b>Testing:</b> {testing}<br/>" \
            "<b>Debug:</b> {debug}<br/>"
    return html.format(testing=current_app.config['TESTING'],
                       debug=current_app.config['DEBUG'])

