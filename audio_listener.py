from time import sleep

import sounddevice as sd
from audio_recorder import AudioRecorder
from dtmf import DTMFDetector

SAMPLE_RATE = 8000 #todo
BLOCK_SIZE = 1024


class AudioListener:

    def __init__(
            self,
            microphone_index,
            dtmf_callback,
            record_callback
    ):
        self.microphone_index = microphone_index

        self.dtmf_service = DTMFDetector(
            callback=dtmf_callback,
        )

        self.recorder_service = AudioRecorder(
            callback=record_callback
        )

    def record(self):
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=self.audio_callback, blocksize=BLOCK_SIZE, device=self.microphone_index):
            self.recorder_service.loop_checker()

    def audio_callback(self, indata, frames, time_info, status):
        self.dtmf_service.audio_callback(indata, frames, time_info, status)
        self.recorder_service.audio_callback(indata, frames, time_info, status)