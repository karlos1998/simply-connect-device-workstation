import requests
import config
from SimplyError import SimplyError


class SimplyConnectAPI:

    api_key = None

    base_url = config.server_url + "/workstation"

    device_id = None

    @staticmethod
    def get_headers():
        return {
            "Authorization": f"Bearer {SimplyConnectAPI.api_key}",
            "Content-Type": "application/json"
        }

    def get_headers_with_device_id(self):
        headers = SimplyConnectAPI.get_headers()
        headers["X-Device-Id"] = self.device_id
        return headers


    def send_dtmf_tone(self, tone, audio_is_playing):
        url = f"{SimplyConnectAPI.base_url}/current-call/tone"
        data = {"tone": tone, "audio_is_playing": audio_is_playing}
        try:
            response = requests.post(url, headers=self.get_headers_with_device_id(), json=data)
            response.raise_for_status()  # Sprawdź, czy wystąpił błąd
            return response.json().get("node")
        except Exception as e:
            print(f"Błąd podczas wysyłania tonu DTMF: {e}")

    def send_audio_fragment(self, audio_file_path, detected_speech, audio_is_playing):
        url = f"{SimplyConnectAPI.base_url}/current-call/audio"
        params = {
            "detected_speech": "1" if detected_speech else "0",
            "audio_is_playing": "1" if audio_is_playing else "0"
        }
        url_with_params = f"{url}?detected_speech={params['detected_speech']}&audio_is_playing={params['audio_is_playing']}"

        with open(audio_file_path, "rb") as audio_file:
            files = {
                "audio": (audio_file_path, audio_file, "audio/mp2t"),
            }

            headers = {
                "Authorization": f"Bearer {SimplyConnectAPI.api_key}",
                "Accept": "application/json",
                "X-Device-Id": self.device_id,
            }

            try:
                # Przesyłanie pliku audio z parametrami GET w URL
                response = requests.post(url_with_params, headers=headers, files=files)
                response.raise_for_status()
                # response_data = response.json()
                # print(response_data)
            except Exception as e:
                print("Błąd podczas wysyłania audio do serwera:", e)


    @staticmethod
    def login(auth_key):
        url = f"{SimplyConnectAPI.base_url}/login"
        data = {
            "auth_key": auth_key
        }
        try:
            response = requests.post(url, headers=SimplyConnectAPI.get_headers(), json=data)
            SimplyConnectAPI.api_key = response.json().get("token")
            return SimplyConnectAPI.api_key
        except Exception as e:
            raise SimplyError(f"Bład logowania: {e}")

    @staticmethod
    def update_audio_devices_list(devices):
        url = f"{SimplyConnectAPI.base_url}/audio-devices"
        data = {
            "devices": devices
        }
        try:
            response = requests.put(url, headers=SimplyConnectAPI.get_headers(), json=data)
        except Exception as e:
            print("Błąd przesyłania listy urządzeń")
            print(e)

    @staticmethod
    def get_devices():
        url = f"{SimplyConnectAPI.base_url}/devices"
        try:
            return requests.get(url, headers=SimplyConnectAPI.get_headers()).json()
        except Exception as e:
            print("Błąd podczas pobierania listy urządzeń")
            print(e)

    def update_device(self, input_audio_device_index, output_audio_device_index):
        url = f"{SimplyConnectAPI.base_url}/device"
        data = {
            "input_audio_device_index": input_audio_device_index,
            "output_audio_device_index": output_audio_device_index
        }
        try:
            response = requests.patch(url, headers=self.get_headers_with_device_id(), json=data)
            response.raise_for_status()  # Sprawdź, czy wystąpił błąd
        except Exception as e:
            print(f"Błąd podczas zaktualizowanych danych: {e}")

    def get_first_conversation_tree_node(self):
        url = f"{SimplyConnectAPI.base_url}/current-call/current-conversation-tree"
        try:
            response = requests.get(url, headers=self.get_headers_with_device_id())
            response.raise_for_status()  # Sprawdź, czy wystąpił błąd
            return response.json().get("node")
        except Exception as e:
            print(f"Błąd podczas pobierania pierwszego node: {e}")

    def go_to_next_conversation_tree_step(self, waiting_time, current_node_id):
        url = f"{SimplyConnectAPI.base_url}/current-call/conversation-tree-next-step"
        data = {"waiting_time": waiting_time, "current_node_id": current_node_id}
        response = requests.post(url, headers=self.get_headers_with_device_id(), json=data)
        response.raise_for_status()
        return response.json().get("node")

    def get_conversation_tree_node_additional_audio(self):
        url = f"{SimplyConnectAPI.base_url}/current-call/conversation-tree-node-additional-audio"
        try:
            response = requests.get(url, headers=self.get_headers_with_device_id())
            response.raise_for_status()
            if response.status_code == 200: #200 - has file path, 201 - no content (no file path :D )
                return response.json().get("file_path")
            return None
        except Exception as e:
            return None
