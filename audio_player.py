from pydub import AudioSegment
import numpy as np
import sounddevice as sd
import threading

class AudioPlayer:
    def __init__(self, output_device_index):
        self.output_device_index = output_device_index
        self.is_playing = False
        self.stream = None

    def play(self, file_path, callback):
        def play_audio():
            self.is_playing = True
            try:
                audio = AudioSegment.from_file(file_path)

                channels = audio.channels

                samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0

                if channels > 1:
                    samples = np.reshape(samples, (-1, channels))

                with sd.OutputStream(device=self.output_device_index, channels=channels) as stream:
                    self.stream = stream

                    try:
                        stream.write(samples)
                        sd.wait()
                    except sd.PortAudioError as e:
                        if e.args[0] != -9986:  # blad po przerwaniu odtwarzania metoda .stop() - trzeba zignorowac
                            raise e

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
