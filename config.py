import os
from dotenv import load_dotenv

load_dotenv()

pusher_host = os.getenv('PUSHER_HOST')
pusher_app_key = os.getenv('PUSHER_APP_KEY')

server_url = os.getenv('SERVER_URL')

auth_key=os.getenv('AUTH_KEY')