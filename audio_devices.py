import sounddevice as sd
import uuid

class AudioDevices:
    devices = []

    @staticmethod
    def __generate_uuid(device, role):
        unique_string = (
            f"{device['name']}-{device['hostapi']}-"
            f"{device['max_input_channels'] if role == 'input' else device['max_output_channels']}-"
            f"{device['default_low_input_latency'] if role == 'input' else device['default_low_output_latency']}-"
            f"{device['default_samplerate']}"
        )
        return uuid.uuid5(uuid.NAMESPACE_DNS, unique_string).__str__()

    @staticmethod
    def get_list():
        devices = sd.query_devices()
        AudioDevices.devices = []

        for i, device in enumerate(devices):
            # Tworzenie wpisu dla funkcji wejściowej, jeśli urządzenie ma wejścia
            if device['max_input_channels'] > 0:
                input_device = device.copy()
                input_device["type"] = "input"
                input_device["uuid"] = AudioDevices.__generate_uuid(device, "input")
                input_device["index"] = i  # Zapisz indeks dla referencji
                AudioDevices.devices.append(input_device)

            # Tworzenie wpisu dla funkcji wyjściowej, jeśli urządzenie ma wyjścia
            if device['max_output_channels'] > 0:
                output_device = device.copy()
                output_device["type"] = "output"
                output_device["uuid"] = AudioDevices.__generate_uuid(device, "output")
                output_device["index"] = i  # Zapisz indeks dla referencji
                AudioDevices.devices.append(output_device)

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
