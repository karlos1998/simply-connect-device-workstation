import queue
import time

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 8000 #todo


BLOCK_SIZE = 1024
RMS_THRESHOLD = 0.01

def calculate_rms(data):
    """Oblicz RMS dla danych audio."""
    return np.sqrt(np.mean(np.square(data)))



class AudioRecorder:

    audio_queue = queue.Queue()

    last_callback_time = time.time()

    def __init__(self, callback):
        self.microphone_index = None
        self.callback = callback
        self.is_talking = False

    def set_microphone(self, microphone_index):
        self.microphone_index = microphone_index

    def record(self):
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=self.audio_callback, blocksize=BLOCK_SIZE, device=self.microphone_index):
            self.loop_checker()

    def loop_checker(self):
        while True:
            #time.sleep(SILENCE_DURATION)
            time_now = time.time()
            if not self.audio_queue.empty() and (self.audio_queue.qsize() > 20 or (time_now - self.last_callback_time >= 5)):
                audio_data = []
                while not self.audio_queue.empty():
                    audio_data.append(self.audio_queue.get())

                audio_data_concat = np.concatenate(audio_data, axis=0)

                detected_speach = self.is_talking

                self.is_talking = False

                self.last_callback_time = time_now

                self.callback(audio_data_concat, detected_speach)

    def audio_callback(self, indata, frames, time_info, status):

        rms_value = calculate_rms(indata)

        # Wykrywanie mowy
        if rms_value > RMS_THRESHOLD:
            if not self.is_talking:
                self.is_talking = True

        self.audio_queue.put(indata.copy())