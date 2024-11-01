from pydub import AudioSegment
from pydub.effects import compress_dynamic_range, normalize, low_pass_filter, high_pass_filter
import numpy as np
import sounddevice as sd
import threading
import requests
from io import BytesIO

class AudioPlayer:
    def __init__(self, output_device_index, output_device_samplerate):
        self.output_device_index = output_device_index
        self.output_device_samplerate = int(output_device_samplerate)  # Konwertujemy na int, aby unikać błędów
        self.is_playing = False
        self.stream = None
        self.audio_cache = {}

    def add_to_cache(self, url):
        if url not in self.audio_cache:
            response = requests.get(url)
            response.raise_for_status()
            audio = AudioSegment.from_file(BytesIO(response.content))

            # Convert the audio to match the output device sample rate
            if audio.frame_rate != self.output_device_samplerate:
                audio = audio.set_frame_rate(self.output_device_samplerate)

            # Apply various audio effects
            audio = high_pass_filter(audio, 300)
            audio = low_pass_filter(audio, 3400)
            audio = normalize(audio)
            audio = compress_dynamic_range(audio, threshold=-20.0)
            audio = audio.apply_gain(5)

            # Enhance mid frequencies
            mid_freq_audio = high_pass_filter(low_pass_filter(audio, 2000), 600)
            mid_freq_audio = mid_freq_audio.apply_gain(3)
            audio = audio.overlay(mid_freq_audio)

            # Prepare numpy samples
            channels = audio.channels
            samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0

            if channels > 1:
                samples = np.reshape(samples, (-1, channels))

            # Cache processed audio
            self.audio_cache[url] = {
                "samples": samples,
                "channels": channels,
                "sample_rate": int(audio.frame_rate)
            }

    def play(self, url, callback):
        def play_audio():
            self.stop()
            self.is_playing = True
            try:
                if url not in self.audio_cache:
                    self.add_to_cache(url)
                    print("Add audio to cache: " + url)
                else:
                    print("Using cached audio: " + url)

                # Retrieve cached audio data
                cached_audio = self.audio_cache[url]
                samples = cached_audio["samples"]
                channels = cached_audio["channels"]
                sample_rate = cached_audio["sample_rate"]

                # Play audio
                with sd.OutputStream(device=self.output_device_index, channels=channels, samplerate=sample_rate) as stream:
                    self.stream = stream
                    try:
                        stream.write(samples)
                        sd.wait()
                    except sd.PortAudioError:
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
