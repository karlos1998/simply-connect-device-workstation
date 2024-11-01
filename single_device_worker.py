import threading
import time

import numpy as np
from audio_devices import AudioDevices
from audio_listener import AudioListener
from audio_player import AudioPlayer
from conversation_tree import ConversationTree
from simply_connect_api import SimplyConnectAPI

class SingleDeviceWorker:
    def __init__(self, device, pusher_client):

        self.conversation_tree = None

        self.pusher_client = pusher_client

        print("Loaded device: ")
        print(device)

        self.device_id = device["device_id"].__str__()

        self.simply_connect_api_instance = SimplyConnectAPI()
        self.simply_connect_api_instance.device_id = self.device_id

        self.input_audio_device = None
        self.output_audio_device = None

        self.call_status = 'IDLE'


        if device["audio_devices"]:
            # AUDIO INPUT
            input_audio_device = device["audio_devices"]["input"] if "input" in device["audio_devices"] else None
            if input_audio_device:
                self.input_audio_device = AudioDevices.find_device_by_data(input_audio_device, "input")
                if self.input_audio_device:
                    print("Input audio index found: " + self.input_audio_device['index'].__str__())
                    audio_listener = AudioListener(
                        device_worker=self
                    )
                    audio_listener_thread = threading.Thread(target=audio_listener.record)
                    audio_listener_thread.daemon = True
                    audio_listener_thread.start()

            # AUDIO OUTPUT
            output_audio_device = device["audio_devices"]["output"] if "output" in device["audio_devices"] else None
            if output_audio_device:
                self.output_audio_device = AudioDevices.find_device_by_data(output_audio_device, "output")
                if self.output_audio_device:
                    print("Output audio index found: " + self.output_audio_device['index'].__str__())
                    self.audio_player = AudioPlayer(
                        output_device_index=self.output_audio_device['index'],
                        output_device_samplerate=self.output_audio_device['default_samplerate'],
                    )

            self.simply_connect_api_instance.update_device(
                input_audio_device_index=self.input_audio_device['index'],
                output_audio_device_index=self.output_audio_device['index'],
            )

        self.init_pusher_channel()


    def init_pusher_channel(self):
        channel_name = "device." + self.device_id + ".call-status"
        device_private_channel = self.pusher_client.subscribe_private(channel_name=channel_name,
                                        callback_success=lambda: print("[" + self.device_id+ "] Private channel subscription succeeded"),
                                        callback_fail=lambda err: print(f"[" + self.device_id + "] Failed to subscribe to private channel: {err}"))

        device_private_channel.bind(r"App\Events\CallStatusChanged", callback=self.call_status_changed)

    def call_status_changed(self, data):
        self.call_status = data.get("call", {}).get("status", None)
        print("Call status changed: " + self.call_status)
        if self.call_status == 'OFFHOOK':

            if self.audio_player:
                self.audio_player.stop()

            if self.conversation_tree:
                self.conversation_tree.break_tree()
                self.conversation_tree = None

            if self.audio_player:
                node = self.simply_connect_api_instance.get_first_conversation_tree_node()
                if node is not None and self.conversation_tree is None:
                    print("URUCHAMIANIE DRZEWKA ROZMOWY")
                    self.conversation_tree = ConversationTree(self)
                    time.sleep(1)
                    self.conversation_tree.run_node(node)

        if self.call_status == 'IDLE':
            if self.audio_player:
                self.audio_player.stop()