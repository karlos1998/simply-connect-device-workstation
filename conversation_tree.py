import asyncio
import time


class ConversationTree:
    def __init__(self, device_worker):
        self.device_worker = device_worker
        self.broken = False
        self.stop_loop = False

        self.additional_file_path = None
        self.additional_file_processing = False

    def break_tree(self):
        self.broken = True
        self.stop_loop = True

    async def get_additional_node_text(self):
        print("Get additional node text")
        self.additional_file_processing = True
        self.additional_file_path = self.device_worker.simply_connect_api_instance.get_conversation_tree_node_additional_audio()
        if self.additional_file_path is not None:
            print("additional file path")
            print(self.additional_file_path)
            self.device_worker.audio_player.add_to_cache(self.additional_file_path)

        self.additional_file_processing = False

    def run_node(self, node):
        if self.broken:
            return

        self.stop_loop = True

        print("run node: ")
        print(node)

        asyncio.run(self.get_additional_node_text())

        file_audio = node.get("fileAudio")
        if file_audio is not None:
            self.device_worker.audio_player.play(file_audio.get("url"), callback=lambda: self.audio_stopped(node.get("id")))
        elif node.get("type") == "output":
            print("Rozmowa zostala zakonczona - node zwrocil type output")
            pass  # todo - rozmowa zakonczona. serwer sam ja zamknie z telefonem, ale czy tu trzeba cos robic?
        else:
            self.go_to_next_step(node.get("id"))

    def audio_stopped(self, current_node_id):
        print("Odtwrzanie dzwieku zakonczone.")
        if self.device_worker.call_status == 'OFFHOOK':
            if self.additional_file_processing is True:
                tmp_time=time.time()
                while self.additional_file_processing is True and (time.time() - tmp_time) < 15:
                    print("Czekam az additional file skonczy processing...")
                    time.sleep(0.1)

            if self.additional_file_path and self.additional_file_processing is False:
                print("uruchamiam dodatkowy plik audio dla node")
                self.device_worker.audio_player.play(self.additional_file_path, callback=lambda: self.audio_stopped(current_node_id))
                self.additional_file_path = None
            elif self.additional_file_processing is True:
                print("Warning.... Chcialem uruchomic additional file, ale za dlugo to trwalo, wiec pomijam") #todo! moze powinno przerywac rozmowe?
                print("Wiec pora na kolejny krok")
                self.go_to_next_step(current_node_id)
            else:
                print("Pora na kolejny krok")
                self.go_to_next_step(current_node_id)
        else:
            print("Status rozmowy zmienil sie - zakonczono drzewko.")

    def go_to_next_step(self, current_node_id):
        self.stop_loop = False

        time_start = time.time()
        time_diff = 0

        while time_diff < 62:

            time_diff = int(time.time() - time_start)

            if self.broken or self.stop_loop:
                return

            try:
                node = self.device_worker.simply_connect_api_instance.go_to_next_conversation_tree_step(time_diff, current_node_id)
            except Exception as e:
                break

            if node is not None:
                self.run_node(node)
                break

            time.sleep(0.9)

    def go_to_next_step_by_dtmf(self, detected_tone):
        print("go to next step by dtmf: " + detected_tone + ", " + ("is_playing" if self.device_worker.audio_player.is_playing else "is_stopped"))
        node = self.device_worker.simply_connect_api_instance.send_dtmf_tone(detected_tone, self.device_worker.audio_player.is_playing)
        if node is not None:
            self.run_node(node)
