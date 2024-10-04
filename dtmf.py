import numpy as np
import sounddevice as sd
import scipy.fftpack
import scipy.signal as signal
import queue
import time

DTMF_FREQUENCIES = {
    (697, 1209): '1', (697, 1336): '2', (697, 1477): '3',
    (770, 1209): '4', (770, 1336): '5', (770, 1477): '6',
    (852, 1209): '7', (852, 1336): '8', (852, 1477): '9',
    (941, 1209): '*', (941, 1336): '0', (941, 1477): '#'
}

MIN_TONE_DURATION = 0.01  # Minimalny czas trwania tonu (50 ms)

def calculate_rms(data):
    return np.sqrt(np.mean(np.square(data)))

def detect_dtmf_tone(frequencies, magnitudes, threshold=50, tolerance=5):
    for (f1, f2), digit in DTMF_FREQUENCIES.items():
        idx1 = np.where(np.isclose(frequencies, f1, atol=tolerance))[0]
        idx2 = np.where(np.isclose(frequencies, f2, atol=tolerance))[0]
        if idx1.size > 0 and idx2.size > 0:
            if magnitudes[idx1].max() > threshold and magnitudes[idx2].max() > threshold:
                return digit
    return None

class DTMFDetector:
    def __init__(self, callback=None, sample_rate=8000):
        self.sample_rate = sample_rate
        self.block_size = None
        self.callback = callback
        self.audio_queue = queue.Queue()
        self.last_detected_tone = None
        self.tone_start_time = None
        self.microphone_index = None

    def set_microphone(self, microphone_index=None, sample_rate=8000, block_size=1024):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.microphone_index = microphone_index

    def audio_callback(self, indata, frames, time_info, status):
        audio_data = indata[:, 0] * 20  # Wzmocnienie sygnału
        self.audio_queue.put(indata.copy())

        filtered_data = self.filter_audio(audio_data)
        magnitudes, frequencies = self.fft_analysis(filtered_data)

        detected_tone = detect_dtmf_tone(frequencies, magnitudes)

        current_time = time.time()

        if detected_tone:
            if detected_tone == self.last_detected_tone:
                # Sprawdź, czy ton trwa wystarczająco długo
                if self.tone_start_time and (current_time - self.tone_start_time) >= MIN_TONE_DURATION:
                    if self.callback:
                        self.callback(detected_tone)
                    self.last_detected_tone = None  # Resetowanie, aby nie powtarzać wywołań callbacku
            else:
                # Nowy ton, rozpocznij liczenie czasu
                self.last_detected_tone = detected_tone
                self.tone_start_time = current_time
        else:
            # Resetowanie jeśli nie wykryto tonu
            self.last_detected_tone = None
            self.tone_start_time = None

    def filter_audio(self, audio_data):
        b, a = signal.butter(4, [600 / (self.sample_rate / 2), 1600 / (self.sample_rate / 2)], btype='band')
        return signal.lfilter(b, a, audio_data)

    def fft_analysis(self, filtered_data):
        magnitudes = np.abs(scipy.fftpack.fft(filtered_data))
        frequencies = scipy.fftpack.fftfreq(len(magnitudes), 1.0 / self.sample_rate)
        positive_freqs = frequencies[:len(frequencies) // 2]
        positive_mags = magnitudes[:len(magnitudes) // 2]
        return positive_mags, positive_freqs

    def start_detection(self):
        with sd.InputStream(samplerate=self.sample_rate, channels=1, callback=self.audio_callback, blocksize=self.block_size, device=self.microphone_index):
            while True:
                sd.sleep(100)
