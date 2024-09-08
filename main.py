import config
from audio_devices import AudioDevices
from pusher_client import PusherClient
from simply_connect_api import SimplyConnectAPI
from single_device_worker import SingleDeviceWorker


def main():

    #Login to Simply Connect
    SimplyConnectAPI.login()

    #Send input/output audio devices to simply connect
    SimplyConnectAPI.update_audio_devices_list(AudioDevices.get_list())

    #Get Devices list
    devices = SimplyConnectAPI.get_devices()


    # Configure socket (pusher)
    pusher_client = PusherClient(host=config.pusher_host, app_key=config.pusher_app_key)
    #Set channel authorize uth (laravel specific route)
    pusher_client.set_auth_details(auth_url=SimplyConnectAPI.base_url + "/broadcasting/auth", bearer_token=SimplyConnectAPI.api_key)


    #After pusher connected
    def on_connect():
        for device in devices:
            print("After socket connect action for device...")
            print(device)
            channel_name = "device." + device['device_id'].__str__() + ".call-status"
            pusher_client.subscribe_private(channel_name=channel_name,
                                            callback_success=lambda: SingleDeviceWorker( device ),
                                            callback_fail=lambda err: print(f"[" + device['device_id'].__str__() + "] Failed to subscribe to private channel: {err}"))

    #Connect with pusher
    pusher_client.connect(on_connect_callback=on_connect)


if __name__ == "__main__":
    main()
