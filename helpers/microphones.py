from time import sleep

import sounddevice as sd

def list_microphones():
    devices = sd.query_devices()

    print("Available devices with details:")
    for idx, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"\nDevice {idx}: {device['name']}")
            print(f"  Max input channels: {device['max_input_channels']}")
            print(f"  Max output channels: {device['max_output_channels']}")
            print(f"  Default sample rate: {device['default_samplerate']} Hz")
            print(f"  Input latency (low, high): {device['default_low_input_latency']}, {device['default_high_input_latency']} seconds")
            print(f"  Output latency (low, high): {device['default_low_output_latency']}, {device['default_high_output_latency']} seconds")

if __name__ == '__main__':
    while True:
        list_microphones()
        sleep(5)
