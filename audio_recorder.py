import queue

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 8000 #todo
api_key="test" #todo


BLOCK_SIZE = 10240 * 2
RMS_THRESHOLD = 0.01

audio_queue = queue.Queue()

is_talking = False

def calculate_rms(data):
    """Oblicz RMS dla danych audio."""
    return np.sqrt(np.mean(np.square(data)))


def audio_callback(indata, frames, time_info, status):
    global is_talking

    rms_value = calculate_rms(indata)

    # Wykrywanie mowy
    if rms_value > RMS_THRESHOLD:
        if not is_talking:
            is_talking = True

    audio_queue.put(indata.copy())




class AudioRecorder:

    def __init__(self, microphone_index, callback):
        self.microphone_index = microphone_index
        self.callback = callback

    def record(self):
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=audio_callback, blocksize=BLOCK_SIZE, device=self.microphone_index):
            self.loop_checker()

    def loop_checker(self):
        global is_talking
        while True:
            #time.sleep(SILENCE_DURATION)
            if not audio_queue.empty():
                audio_data = []
                while not audio_queue.empty():
                    audio_data.append(audio_queue.get())

                audio_data_concat = np.concatenate(audio_data, axis=0)

                detected_speach = is_talking

                is_talking = False

                self.callback(audio_data_concat, detected_speach)