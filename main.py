import sounddevice as sd
import numpy as np
import threading
import queue
import time
import requests
import scipy.fftpack
import scipy.signal as signal
from scipy.io.wavfile import write

api_key = 'TOOD'

# Ustawienia nagrywania
SAMPLE_RATE = 16000
BLOCK_SIZE = 1024
SILENCE_DURATION = 5
RMS_THRESHOLD = 0.01
DTMF_THRESHOLD = 130  # Obniżony próg wykrywania DTMF
DTMF_TOLERANCE = 8    # Zmniejszona tolerancja
DEBOUNCE_TIME = 0.2   # Skrócony czas blokowania po wykryciu tonu

audio_queue = queue.Queue()
is_talking = False
last_detected_time = 0
last_tone = None

# Częstotliwości DTMF
DTMF_FREQUENCIES = {
    (697, 1209): '1', (697, 1336): '2', (697, 1477): '3',
    (770, 1209): '4', (770, 1336): '5', (770, 1477): '6',
    (852, 1209): '7', (852, 1336): '8', (852, 1477): '9',
    (941, 1209): '*', (941, 1336): '0', (941, 1477): '#'
}

def calculate_rms(data):
    """Oblicz RMS dla danych audio."""
    return np.sqrt(np.mean(np.square(data)))

def detect_dtmf_tone(frequencies, magnitudes, threshold=DTMF_THRESHOLD, tolerance=DTMF_TOLERANCE):
    """Wykrywa ton DTMF na podstawie częstotliwości i amplitud."""
    detected_tones = []

    for (f1, f2), digit in DTMF_FREQUENCIES.items():
        idx1 = np.where(np.isclose(frequencies, f1, atol=tolerance))[0]
        idx2 = np.where(np.isclose(frequencies, f2, atol=tolerance))[0]
        if idx1.size > 0 and idx2.size > 0:
            if magnitudes[idx1].max() > threshold and magnitudes[idx2].max() > threshold:
                detected_tones.append(digit)

    return detected_tones

def audio_callback(indata, frames, time_info, status):
    global is_talking, last_detected_time, last_tone

    rms_value = calculate_rms(indata)

    audio_queue.put(indata.copy())

    # Wykrywanie tonów DTMF
    current_time = time.time()
    if current_time - last_detected_time >= DEBOUNCE_TIME:
        audio_data = indata[:, 0] * 10  # Wzmocnienie sygnału
        b, a = signal.butter(4, [600 / (SAMPLE_RATE / 2), 1600 / (SAMPLE_RATE / 2)], btype='band')
        filtered_data = signal.lfilter(b, a, audio_data)

        magnitudes = np.abs(scipy.fftpack.fft(filtered_data))
        frequencies = scipy.fftpack.fftfreq(len(magnitudes), 1.0 / SAMPLE_RATE)

        positive_freqs = frequencies[:len(frequencies) // 2]
        positive_mags = magnitudes[:len(magnitudes) // 2]

        detected_tones = detect_dtmf_tone(positive_freqs, positive_mags)
        if detected_tones and detected_tones != last_tone:
            last_tone = detected_tones
            print(f"Wykryto ton DTMF: {detected_tones}")
            last_detected_time = current_time
            send_dtmf_tone(detected_tones)
        elif not detected_tones:
            last_tone = None

def send_dtmf_tone(tone):
    """Wyślij wykryty ton DTMF do odpowiedniego endpointu."""
    url = "http://192.168.98.109/workstation/tone"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "tone": tone
    }
    try:
        response = requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"Błąd podczas wysyłania tonu DTMF: {e}")

def transcribe_audio():
    while True:
        if not audio_queue.empty():
            audio_data = []
            while not audio_queue.empty():
                audio_data.append(audio_queue.get())

            audio_data_concat = np.concatenate(audio_data, axis=0)
            audio_file_path = "temp.wav"
            write(audio_file_path, SAMPLE_RATE, (audio_data_concat.flatten() * 32767).astype(np.int16))

            with open(audio_file_path, "rb") as audio_file:
                files = {
                    "audio": (audio_file_path, audio_file, "audio/wav")
                }

                headers = {
                    "Authorization": f"Bearer {api_key}",
                }
                data = {
                    "model": "whisper-1",
                    "language": "pl",
                }

                try:
                    response = requests.post("http://192.168.98.109/workstation/audio", headers=headers, files=files, data=data)
                    response_data = response.json()
                except Exception as e:
                    print("Błąd podczas transkrypcji:", e)

def main():
    # Ustaw indeks mikrofonu USB, np. 2 (zmień, jeśli to inny numer)
    usb_microphone_index = 2

    # Rozpocznij nagrywanie w osobnym wątku
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=audio_callback, blocksize=BLOCK_SIZE, device=usb_microphone_index):
        # Wątek do transkrypcji
        transcribe_thread = threading.Thread(target=transcribe_audio)
        transcribe_thread.daemon = True
        transcribe_thread.start()

        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Zatrzymano nagrywanie.")

if __name__ == "__main__":
    main()
