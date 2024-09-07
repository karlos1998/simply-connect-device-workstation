import requests
import config

class SimplyConnectAPI:
    api_key = 'TODO'
    base_url = config.server_url + "/workstation"

    @staticmethod
    def get_headers():
        return {
            "Authorization": f"Bearer {SimplyConnectAPI.api_key}",
            "Content-Type": "application/json"
        }

    @staticmethod
    def send_dtmf_tone(tone):
        url = f"{SimplyConnectAPI.base_url}/tone"
        data = {"tone": tone}
        try:
            response = requests.post(url, headers=SimplyConnectAPI.get_headers(), json=data)
            response.raise_for_status()  # Sprawdź, czy wystąpił błąd
        except Exception as e:
            print(f"Błąd podczas wysyłania tonu DTMF: {e}")

    @staticmethod
    def send_audio_fragment(audio_file_path, detected_speech):
        url = f"{SimplyConnectAPI.base_url}/audio"

        # Wczytaj plik audio i wyślij do API
        with open(audio_file_path, "rb") as audio_file:
            files = {
                "audio": (audio_file_path, audio_file, "audio/wav")
            }

            headers = {
                "Authorization": f"Bearer {SimplyConnectAPI.api_key}",
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
            return response.json().get("token")
        except Exception as e:
            print(f"Bład logowania: {e}")