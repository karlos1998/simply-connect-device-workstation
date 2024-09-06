import websocket
import json
import requests
import threading
import time

class PusherClient:
    def __init__(self, host, app_key):
        self.host = host
        self.app_key = app_key
        self.ws = None
        self.auth_token = None
        self.auth_url = None
        self.bearer_token = None
        self.socket_id = None
        self.ping_interval = None
        self.ping_thread = None
        self.on_connect_callback = None

        # Przechowywanie callbacków dla każdego kanału
        self.callbacks = {}

    def set_auth_details(self, auth_url, bearer_token):
        """
        Sets the authorization URL and Bearer token for private channels.
        """
        self.auth_url = auth_url
        self.bearer_token = bearer_token

    def on_message(self, ws, message):
        """
        Handles incoming WebSocket messages.
        """
        print(f"Received message: {message}")
        data = json.loads(message)
        event = data.get("event")
        channel = data.get("channel")

        if event == "pusher:connection_established":
            connection_data = json.loads(data["data"])
            self.socket_id = connection_data["socket_id"]
            self.ping_interval = connection_data.get("activity_timeout", 30)
            print(f"Connection established. socket_id: {self.socket_id}, ping interval: {self.ping_interval} seconds")

            # Start pinging the server
            self.start_pinging()

            # Trigger the connection callback
            if self.on_connect_callback:
                self.on_connect_callback()

        # Handle subscription success or failure
        elif event == "pusher_internal:subscription_succeeded":
            if channel in self.callbacks:
                if self.callbacks[channel]["success"]:
                    self.callbacks[channel]["success"]()

        elif event == "pusher:subscription_error":
            error_data = data.get("data", {})
            if channel in self.callbacks:
                if self.callbacks[channel]["fail"]:
                    self.callbacks[channel]["fail"](error_data)

    def on_error(self, ws, error):
        """
        Handles WebSocket errors.
        """
        print(f"Error occurred: {error}")

    def on_close(self, ws, _, __):
        """
        Handles WebSocket closing.
        """
        print("Connection closed")
        self.stop_pinging()

    def on_open(self, ws):
        """
        Handles WebSocket opening.
        """
        print("Connected to the server")

    def connect(self, on_connect_callback=None):
        """
        Initiates a WebSocket connection. Takes an optional callback, which is called when the connection is established.
        """
        self.on_connect_callback = on_connect_callback
        url = f"wss://{self.host}/app/{self.app_key}?protocol=7&client=js&version=8.4.0-rc2&flash=false"
        self.ws = websocket.WebSocketApp(url,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open

        socket_thread = threading.Thread(target=self.ws.run_forever)
        socket_thread.start()

    def start_pinging(self):
        """
        Starts a thread to send ping messages at regular intervals.
        """
        def ping():
            while self.ws and self.ws.sock and self.ws.sock.connected:
                self.ws.send(json.dumps({"event": "pusher:ping", "data": {}}))
                print("Ping sent")
                time.sleep(self.ping_interval)

        self.ping_thread = threading.Thread(target=ping)

        time.sleep(self.ping_interval)
        self.ping_thread.start()

    def stop_pinging(self):
        """
        Stops the ping thread.
        """
        if self.ping_thread and self.ping_thread.is_alive():
            self.ping_thread.join()

    def get_auth_token(self, channel_name):
        """
        Sends an authorization request to the set URL and retrieves the token.
        """
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Accept": "application/json"
        }
        data = {
            "socket_id": self.socket_id,
            "channel_name": f"private-{channel_name}"
        }

        response = requests.post(self.auth_url, headers=headers, json=data)

        if response.status_code == 200:
            auth_data = response.json()
            return auth_data["auth"]
        else:
            print(f"Authorization failed: {response.status_code}")
            return None

    def subscribe_public(self, channel_name, callback_success=None, callback_fail=None):
        """
        Subscribes to a public channel with optional success and failure callbacks.
        """
        if self.ws:
            self.callbacks[channel_name] = {
                "success": callback_success,
                "fail": callback_fail
            }

            subscribe_data = {
                "event": "pusher:subscribe",
                "data": {
                    "channel": channel_name
                }
            }
            self.ws.send(json.dumps(subscribe_data))
            print(f"Subscribed to public channel: {channel_name}")
        else:
            error_json = {"error": "No active WebSocket connection"}
            print("No active WebSocket connection")
            if callback_fail:
                callback_fail(error_json)

    def subscribe_private(self, channel_name, callback_success=None, callback_fail=None):
        """
        Subscribes to a private channel after authorization, with optional success and failure callbacks.
        """
        if self.ws:

            private_channel = f"private-{channel_name}"

            self.callbacks[private_channel] = {
                "success": callback_success,
                "fail": callback_fail
            }

            # Retrieve the authorization token
            auth_token = self.get_auth_token(channel_name)
            if auth_token:
                subscribe_data = {
                    "event": "pusher:subscribe",
                    "data": {
                        "auth": auth_token,
                        # Additional user data can be added here
                        "channel": private_channel
                    }
                }
                self.ws.send(json.dumps(subscribe_data))
                print(f"Subscribed to private channel: {private_channel}")
            else:
                error_json = {"error": "Authorization failed"}
                print("Authorization failed")
                if callback_fail:
                    callback_fail(error_json)
        else:
            error_json = {"error": "No active WebSocket connection"}
            print("No active WebSocket connection")
            if callback_fail:
                callback_fail(error_json)
