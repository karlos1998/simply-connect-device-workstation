import time


class ConversationTree:
    def __init__(self, device_worker):
        self.device_worker = device_worker
        self.broken = False

    def break_tree(self):
        self.broken = True

    def run_node(self, node):

        if self.broken:
            return

        file_audio = node.get("fileAudio")
        if file_audio is not None:
            self.device_worker.audio_player.play(file_audio.get("url"), callback=self.audio_stopped)
        elif node.get("type") == "output":
            print("Rozmowa zostala zakonczona - node zwrocil type output")
            pass #todo - rozmowa zakonczona. serwer sam ja zamknie z telefonem, ale czy tu trzeba cos robic ?
        else:
            self.go_to_next_step()

    def audio_stopped(self):
        print("Odtwrzanie dzwieku zakonczone.")
        if self.device_worker.call_status == 'OFFHOOK':
            print("Pora na kolejny krok")
            self.go_to_next_step()
        else:
            print("Status rozmowy zmienil sie - zakonczono drzewko.")

    def go_to_next_step(self):
        for i in range(1, 62):

            if self.broken:
                return

            node = self.device_worker.simply_connect_api_instance.go_to_next_conversation_tree_step(i)
            if node is not None:
                self.run_node(node)
                break
            time.sleep(1)
