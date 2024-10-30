from threading import Thread
from time import sleep
import sounddevice as sd
import uuid

class AudioDevices:
    devices = []

    @staticmethod
    def __generate_uuid(device):
        unique_string = (
            f"{device['name']}-{device['hostapi']}-"
            f"{device['max_input_channels']}-{device['max_output_channels']}-"
            f"{device['default_low_input_latency']}-{device['default_low_output_latency']}-"
            f"{device['default_high_input_latency']}-{device['default_high_output_latency']}-"
            f"{device['default_samplerate']}"
        )
        return uuid.uuid5(uuid.NAMESPACE_DNS, unique_string).__str__()

    @staticmethod
    def get_list():
        devices = sd.query_devices()
        AudioDevices.devices = []
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0 and device['max_output_channels'] > 0:
                device_type = "hybrid"
            elif device['max_input_channels'] > 0:
                device_type = "input"
            else:
                device_type = "output"

            device_uuid = AudioDevices.__generate_uuid(device)
            device["type"] = device_type
            device["uuid"] = device_uuid
            device["index"] = i  # Dodajemy index urządzenia
            AudioDevices.devices.append(device)
        return AudioDevices.devices

    @staticmethod
    def find_device_index_by_data(data, audio_type):
        for audio_device in AudioDevices.devices:
            if audio_device["uuid"] == data["uuid"] and audio_device["type"] == audio_type:
                print("Audio device found by uuid")
                return audio_device["index"]

        for audio_device in AudioDevices.devices:
            if audio_device["name"] == data["name"] and audio_device["type"] == audio_type:
                print("Audio device found by name")
                return audio_device["index"]

        return None
