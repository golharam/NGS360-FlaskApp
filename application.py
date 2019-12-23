from os.path import dirname, join
from dotenv import load_dotenv
from app import create_app

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

application = create_app()

# Run the application
if __name__ == "__main__":
    application.run(host="0.0.0.0")
