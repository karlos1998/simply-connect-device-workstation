from pydub import AudioSegment
from pydub.effects import compress_dynamic_range, normalize, low_pass_filter, high_pass_filter
import numpy as np
import sounddevice as sd
import threading
import requests
from io import BytesIO

class AudioPlayer:
    def __init__(self, output_device_index):
        self.output_device_index = output_device_index
        self.is_playing = False
        self.stream = None
        self.audio_cache = {}  # Cache na przechowywanie przetworzonych plików audio

    def play(self, url, callback):
        def play_audio():
            self.stop()
            self.is_playing = True
            try:
                # Sprawdź, czy plik jest już w cache
                if url in self.audio_cache:
                    audio = self.audio_cache[url]
                else:
                    # Pobieranie pliku audio z URL
                    response = requests.get(url)
                    response.raise_for_status()

                    # Wczytywanie audio z bajtów
                    audio = AudioSegment.from_file(BytesIO(response.content))

                    # Przetwarzanie audio - przygotowanie do odtwarzania przez telefon
                    audio = high_pass_filter(audio, 300)  # Filtr górnoprzepustowy, aby pozbyć się częstotliwości poniżej 300 Hz
                    audio = low_pass_filter(audio, 3400)  # Filtr dolnoprzepustowy, aby ograniczyć częstotliwości powyżej 3400 Hz
                    audio = normalize(audio)  # Normalizacja poziomu głośności
                    audio = compress_dynamic_range(audio, threshold=-20.0)  # Kompresja dynamiczna
                    audio = audio.apply_gain(5)  # Wzmocnienie o 5 dB

                    # Dodatkowe wzmocnienie wybranego pasma częstotliwości
                    mid_freq_audio = high_pass_filter(low_pass_filter(audio, 2000), 600)  # Wzmocnienie pasma 600-2000 Hz
                    mid_freq_audio = mid_freq_audio.apply_gain(3)  # Zwiększenie głośności wybranego pasma
                    audio = audio.overlay(mid_freq_audio)  # Połączenie ze zmodyfikowanym sygnałem

                    # Dodaj przetworzony plik audio do cache
                    self.audio_cache[url] = audio

                channels = audio.channels
                sample_rate = audio.frame_rate

                # Konwersja próbek audio do formatu numpy.float32
                samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0

                # Jeśli audio jest wielokanałowe, przekształć do odpowiedniego kształtu
                if channels > 1:
                    samples = np.reshape(samples, (-1, channels))

                # Konfigurowanie strumienia wyjściowego z poprawnym sample rate
                with sd.OutputStream(device=self.output_device_index, channels=channels, samplerate=sample_rate) as stream:
                    self.stream = stream

                    try:
                        stream.write(samples)
                        sd.wait()
                    except sd.PortAudioError as e:
                        # if e.args[0] != -9986:  # blad po przerwaniu odtwarzania metoda .stop() - trzeba zignorowac
                        #     raise e
                        pass

            finally:
                self.is_playing = False
                self.stream = None
                if callback:
                    callback()

        threading.Thread(target=play_audio).start()

    def stop(self):
        if self.stream and self.is_playing:
            self.stream.abort()
            self.is_playing = False
