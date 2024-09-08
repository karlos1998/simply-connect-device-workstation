import requests
import config

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


    def send_dtmf_tone(self, tone):
        url = f"{SimplyConnectAPI.base_url}/tone"
        data = {"tone": tone}
        try:
            response = requests.post(url, headers=self.get_headers_with_device_id(), json=data)
            response.raise_for_status()  # Sprawdź, czy wystąpił błąd
        except Exception as e:
            print(f"Błąd podczas wysyłania tonu DTMF: {e}")

    def send_audio_fragment(self, audio_file_path, detected_speech):
        url = f"{SimplyConnectAPI.base_url}/audio"

        # Wczytaj plik audio i wyślij do API
        with open(audio_file_path, "rb") as audio_file:
            files = {
                "audio": (audio_file_path, audio_file, "audio/mp2t")
            }

            headers = {
                "Authorization": f"Bearer {SimplyConnectAPI.api_key}",
                "Accept": "application/json", #todo - pobierac normalnie naglowki i dac jakies.. without content-type czy cos
                "X-Device-Id": self.device_id,
            }

            # Tworzenie danych jako osobny obiekt JSON
            data = {
                "detected_speech": 1 if detected_speech else 0
            }

            try:
                # Użyj `files` do przesyłania pliku audio oraz `data` do przesyłania danych
                response = requests.post(url, headers=headers, files=files, data=data)
                response_data = response.json()
                print(response_data)
            except Exception as e:
                print("Błąd podczas wysyłania audio do serwera:", e)

    @staticmethod
    def login():
        url = f"{SimplyConnectAPI.base_url}/login"
        data = {}
        try:
            response = requests.post(url, headers=SimplyConnectAPI.get_headers(), json=data)
            SimplyConnectAPI.api_key = response.json().get("token")
            return SimplyConnectAPI.api_key
        except Exception as e:
            print(f"Bład logowania: {e}")

    @staticmethod
    def update_audio_devices_list(devices):
        url = f"{SimplyConnectAPI.base_url}/audio/devices"
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