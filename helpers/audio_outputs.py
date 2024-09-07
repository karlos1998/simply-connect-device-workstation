import sounddevice as sd
from pydub import AudioSegment
import numpy as np

import sounddevice as sd
import uuid

def generate_uuid(device):
    # Generowanie UUID na podstawie bardziej szczegółowych właściwości urządzenia
    unique_string = (
        f"{device['name']}-{device['hostapi']}-"
        f"{device['max_input_channels']}-{device['max_output_channels']}-"
        f"{device['default_low_input_latency']}-{device['default_low_output_latency']}-"
        f"{device['default_high_input_latency']}-{device['default_high_output_latency']}-"
        f"{device['default_samplerate']}"
    )
    return uuid.uuid5(uuid.NAMESPACE_DNS, unique_string)

def list_audio_devices():
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        device_type = "Głośnik" if device['max_output_channels'] > 0 else "Mikrofon"
        device_uuid = generate_uuid(device)
        print(device)
        print(f"{i}: {device['name']}, Typ: {device_type}, "
              f"Channels: {device['max_output_channels']} out / {device['max_input_channels']} in, "
              f"Sample Rate: {device['default_samplerate']} Hz, UUID: {device_uuid}")

def play_audio(file_path, output_device):
    # Wybór urządzenia wyjściowego
    sd.default.device = output_device

    # Wczytanie pliku audio
    audio = AudioSegment.from_file(file_path)

    # Konwersja audio na typ float32, który jest zgodny z sounddevice
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0  # Normalizacja do zakresu -1 do 1

    # Jeśli plik jest stereo, musimy dostosować do 2 kanałów
    if audio.channels == 2:
        samples = np.reshape(samples, (-1, 2))

    # Odtwarzanie dźwięku
    sd.play(samples, samplerate=audio.frame_rate)
    sd.wait()

# Przykład użycia
list_audio_devices()  # Wyświetla listę dostępnych urządzeń wyjściowych

device_index = int(input("Podaj numer urządzenia wyjściowego: "))  # Użytkownik wybiera urządzenie
play_audio("file.m4a", device_index)  # Odtwarza plik na wybranym urządzeniu
