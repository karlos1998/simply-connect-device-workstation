from threading import Thread
from time import sleep

import sounddevice as sd
import uuid

class AudioDevices:

    devices = []

    @staticmethod
    def __generate_uuid(device):
        # Generowanie UUID na podstawie bardziej szczegółowych właściwości urządzenia
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
            device_type = "output" if device['max_output_channels'] > 0 else "input"
            device_uuid = AudioDevices.__generate_uuid(device)
            device["type"] = device_type
            device["uuid"] = device_uuid
            AudioDevices.devices.append(device)
            # print(device)
            # print(f"{i}: {device['name']}, Typ: {device_type}, "
            #       f"Channels: {device['max_output_channels']} out / {device['max_input_channels']} in, "
            #       f"Sample Rate: {device['default_samplerate']} Hz, UUID: {device_uuid}")
        return AudioDevices.devices



