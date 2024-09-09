from pydub import AudioSegment
import numpy as np
import sounddevice as sd

class AudioPlayer:
    def __init__(self, output_device_index):
        self.output_device_index = output_device_index

    def play(self, file_path):
        # Wybór urządzenia wyjściowego
        sd.default.device = self.output_device_index #todo - trzeba zweryfikowac czy przy wielu watkach, wielu urzadzeniach nie bedzie sie gryzc

        # Wczytanie pliku audio
        audio = AudioSegment.from_file(file_path)

        # Konwersja audio na typ float32, który jest zgodny z sounddevice
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0  # Normalizacja do zakresu -1 do 1

        # Jeśli plik jest stereo, musimy dostosować do 2 kanałów
        if audio.channels == 2:
            samples = np.reshape(samples, (-1, 2))

        # Odtwarzanie dźwięku
        sd.play(samples, samplerate=audio.frame_rate)
        sd.wait()