import sounddevice as sd

def get_audio_devices():
    devices = sd.query_devices()
    inputs = [device for device in devices if device['max_input_channels'] > 0]
    outputs = [device for device in devices if device['max_output_channels'] > 0]
    return inputs, outputs

if __name__ == "__main__":
    inputs, outputs = get_audio_devices()
    print("Dostępne wejścia audio:")
    for idx, device in enumerate(inputs):
        print(f"{idx + 1}. {device['name']} - Kanały wejściowe: {device['max_input_channels']}")

    print("\nDostępne wyjścia audio:")
    for idx, device in enumerate(outputs):
        print(f"{idx + 1}. {device['name']} - Kanały wyjściowe: {device['max_output_channels']}")
