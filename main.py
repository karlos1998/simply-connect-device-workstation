import numpy as np
import sounddevice as sd
import threading
import time

import config
from pusher_client import PusherClient
from simply_connect_api import SimplyConnectAPI
from scipy.io.wavfile import write
from audio_listener import AudioListener

def dtmf_callback(detected_tones):
    SimplyConnectAPI.send_dtmf_tone(detected_tones)


def record_callback(audio_data_concat, is_talking):

    audio_file_path = "temp.wav"
    write(audio_file_path, 8000, (audio_data_concat.flatten() * 32767).astype(np.int16))

    SimplyConnectAPI.send_audio_fragment(audio_file_path, is_talking)

def main():

    login_token=SimplyConnectAPI.login()

    # Connect to socket (pusher)
    pusher_client = PusherClient(host=config.pusher_host, app_key=config.pusher_app_key)
    pusher_client.set_auth_details(auth_url=SimplyConnectAPI.base_url + "/broadcasting/auth", bearer_token=login_token)

    def on_connect():
        pusher_client.subscribe_private("workstation.1",
                                        callback_success=lambda: print("Private channel subscription succeeded"),
                                        callback_fail=lambda err: print(f"Failed to subscribe to private channel: {err}"))

    pusher_client.connect(on_connect_callback=on_connect)




    # Ustaw indeks mikrofonu
    devices = sd.query_devices()
    usb_microphone = next((device for device in devices if "USB Audio" in device['name'] and device['max_input_channels'] > 0), None)

    if usb_microphone is None:
        print("Nie znaleziono odpowiedniego mikrofonu USB z aktywnymi kanałami wejściowymi.")
        return

    usb_microphone_index = devices.index(usb_microphone)
    print(f"Używanie mikrofonu: {usb_microphone['name']}")
    print(f"Indeks urządzenia: {usb_microphone_index}")


    audio_listener = AudioListener(microphone_index=usb_microphone_index, record_callback=record_callback, dtmf_callback=dtmf_callback)

    audio_listener_thread = threading.Thread(target=audio_listener.record)
    audio_listener_thread.daemon = True
    audio_listener_thread.start()




    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Zamykanie aplikacji...")

if __name__ == "__main__":
    main()
