import config
from SimplyError import SimplyError
from audio_devices import AudioDevices
from pusher_client import PusherClient
from simply_connect_api import SimplyConnectAPI
from single_device_worker import SingleDeviceWorker
import colorama
import sys
colorama.init(autoreset=True)

def main():

    try:
        #Login to Simply Connect
        SimplyConnectAPI.login(config.auth_key)

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

            pusher_client.subscribe_presence("work-stations-online")

            for device in devices:
                print("After socket connect action for device...")
                print(device)
                SingleDeviceWorker( device, pusher_client )


        #Connect with pusher
        pusher_client.connect(on_connect_callback=on_connect)
    except SimplyError as e:
        sys.stderr.write(colorama.Fore.RED + str(e) + '\n')
        sys.exit(1)

if __name__ == "__main__":
    main()
