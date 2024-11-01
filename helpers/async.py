import threading
import time

def get_additional_node_text():
    time.sleep(3)


print("start additional text sync")
threading.Thread(target=get_additional_node_text).start()
print("stop additional text sync")
