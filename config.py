import os
from dotenv import load_dotenv

load_dotenv()

pusher_host = ''
pusher_app_key = ''

server_url = os.getenv('SERVER_URL', 'https://panel.simply-connect.ovh')

auth_key=os.getenv('AUTH_KEY')