import sounddevice as sd

def list_microphones():
    devices = sd.query_devices()

    print("Available microphones:")
    for idx, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"{idx}: {device['name']}")

if __name__ == '__main__':
    list_microphones()
