import threading

import numpy as np

from audio_devices import AudioDevices
from audio_listener import AudioListener
from simply_connect_api import SimplyConnectAPI
from scipy.io.wavfile import write

class SingleDeviceWorker:
    def __init__(self, device):

        print("[" + device['device_id'].__str__() + "] Private channel subscription succeeded")

        print("Device audio devices:")

        self.device_id = device["device_id"].__str__()

        self.simply_connect_api_instance = SimplyConnectAPI()
        self.simply_connect_api_instance.device_id = self.device_id

        self.input_audio_device_index = None
        self.output_audio_device_index = None

        input_audio_device = device["audio_devices"]["input"] if "input" in device["audio_devices"] else None
        if input_audio_device:
            self.input_audio_device_index = AudioDevices.find_device_index_by_data(input_audio_device, "input")
            if self.input_audio_device_index:
                print("Input audio index found: " + self.input_audio_device_index.__str__())
                audio_listener = AudioListener(
                    microphone_index=self.input_audio_device_index,
                    record_callback=self.record_callback,
                    dtmf_callback=self.dtmf_callback
                )
                audio_listener_thread = threading.Thread(target=audio_listener.record)
                audio_listener_thread.daemon = True
                audio_listener_thread.start()

        output_audio_device = device["audio_devices"]["output"] if "output" in device["audio_devices"] else None
        if output_audio_device:
            self.output_audio_device_index = AudioDevices.find_device_index_by_data(output_audio_device, "output")

        self.simply_connect_api_instance.update_device(
            input_audio_device_index=self.input_audio_device_index,
            output_audio_device_index=self.output_audio_device_index,
        )



    def dtmf_callback(self, detected_tones):
        self.simply_connect_api_instance.send_dtmf_tone(detected_tones)


    def record_callback(self, audio_data_concat, is_talking):

        # audio_file_path = "temp.ts"
        # write(audio_file_path, 8000, audio_data_concat)

        audio_file_path = self.device_id + "-temp.wav"
        write(audio_file_path, 8000, (audio_data_concat.flatten() * 32767).astype(np.int16))

        self.simply_connect_api_instance.send_audio_fragment(audio_file_path, is_talking)

