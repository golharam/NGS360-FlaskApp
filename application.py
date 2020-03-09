'''
Main application entry point
'''
from os.path import dirname, join
from dotenv import load_dotenv
from app import create_app, DB, BASESPACE
from app.models import BatchJob, Notification, SequencingRun, User

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

application = create_app()

@application.shell_context_processor
def make_shell_context():
    # For this to work, make sure FLASK_APP=application.py is set
    return {'db': DB,
            'BatchJob': BatchJob,
            'Notification': Notification,
            'SequencingRun': SequencingRun,
            'User': User,
            'baseSpace': BASESPACE}

# Run the application
if __name__ == "__main__":
    application.run(host="0.0.0.0")
