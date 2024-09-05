import numpy as np
import sounddevice as sd
import threading
import time
from scipy.io.wavfile import write
import requests

from audio_recorder import AudioRecorder
from dtmf import DTMFDetector
from simply_connect_api import SimplyConnectAPI

api_key = 'TODO' #todo
SAMPLE_RATE = 8000 #todo

def dtmf_callback(detected_tones):
    SimplyConnectAPI.send_dtmf_tone(detected_tones)


def audio_callback(audio_data_concat, is_talking):

    audio_file_path = "temp.wav"
    write(audio_file_path, SAMPLE_RATE, (audio_data_concat.flatten() * 32767).astype(np.int16))

    SimplyConnectAPI.send_audio_fragment(audio_file_path, is_talking)

def calculate_rms(data):
    """Oblicz RMS dla danych audio."""
    return np.sqrt(np.mean(np.square(data)))

def main():

    # Ustaw indeks mikrofonu
    devices = sd.query_devices()
    usb_microphone = next((device for device in devices if "USB Audio" in device['name'] and device['max_input_channels'] > 0), None)

    if usb_microphone is None:
        print("Nie znaleziono odpowiedniego mikrofonu USB z aktywnymi kanałami wejściowymi.")
        return

    usb_microphone_index = devices.index(usb_microphone)
    print(f"Używanie mikrofonu: {usb_microphone['name']}")
    print(f"Indeks urządzenia: {usb_microphone_index}")



    # Rozpoczęcie wykrywania DTMF
    dtmf_detector = DTMFDetector(microphone_index=usb_microphone_index, callback=dtmf_callback)

    dtmf_detection_thread = threading.Thread(target=dtmf_detector.start_detection)
    dtmf_detection_thread.daemon = True
    dtmf_detection_thread.start()


    #Rozpoczęcie zbierania dzwięku

    audio_recorder = AudioRecorder(microphone_index=usb_microphone_index, callback=audio_callback)

    audio_recorder_thread = threading.Thread(target=audio_recorder.record)
    audio_recorder_thread.daemon = True
    audio_recorder_thread.start()


    while True:
        time.sleep(0.1)

if __name__ == "__main__":
    main()
