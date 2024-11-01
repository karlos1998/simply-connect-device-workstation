from time import sleep

import numpy as np
import sounddevice as sd
from audio_recorder import AudioRecorder
from dtmf import DTMFDetector
from scipy.io.wavfile import write

# SAMPLE_RATE = 44100 #todo
BLOCK_SIZE = 1024


class AudioListener:

    def __init__(
            self,
            # microphone_index,
            # dtmf_callback,
            # record_callback
            device_worker
    ):
        # self.microphone_index = microphone_index
        #
        # self.dtmf_service = DTMFDetector(
        #     callback=dtmf_callback,
        # )
        #
        # self.recorder_service = AudioRecorder(
        #     callback=record_callback
        # )

        self.device_worker = device_worker

        self.dtmf_service = DTMFDetector(
            callback=self.dtmf_callback,
            sample_rate=self.device_worker.input_audio_device['default_samplerate'],
        )

        self.recorder_service = AudioRecorder(
            callback=self.record_callback
        )

    def record(self):
        with sd.InputStream(samplerate=int(self.device_worker.input_audio_device['default_samplerate']), channels=1, callback=self.audio_callback, blocksize=BLOCK_SIZE, device=self.device_worker.input_audio_device['index']):
            self.recorder_service.loop_checker()

    def audio_callback(self, indata, frames, time_info, status):

        if not self.device_worker.call_status == "OFFHOOK":
            return #todo - trzeba poprawic dzialanie tego. status rozpoczenia rozmowy "OFFHOOK" przychodzi z kilku sekundowym opoznieniem, dlatego poczatek rozmwowy jest uciety...

        self.dtmf_service.audio_callback(indata, frames, time_info, status)
        self.recorder_service.audio_callback(indata, frames, time_info, status)


    #####################
    def dtmf_callback(self, detected_tone):
        #self.device_worker.simply_connect_api_instance.send_dtmf_tone(detected_tones)
        self.device_worker.conversation_tree.go_to_next_step_by_dtmf(detected_tone)


    def record_callback(self, audio_data_concat, is_talking):

        # audio_file_path = "temp.ts"
        # write(audio_file_path, 8000, audio_data_concat)

        audio_file_path = self.device_worker.device_id + "-temp.wav"
        write(audio_file_path, int(self.device_worker.input_audio_device['default_samplerate']), (audio_data_concat.flatten() * 32767).astype(np.int16))

        print("SEND AUDIO FRAGMENT")

        self.device_worker.simply_connect_api_instance.send_audio_fragment(audio_file_path, is_talking, self.device_worker.audio_player.is_playing)