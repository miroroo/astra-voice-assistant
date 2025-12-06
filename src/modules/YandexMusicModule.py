from src.core.event_bus import EventBus
from yandex_music import Client
from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio
from pydub.playback import play
import os


class YandexMusicModule:
    def __init__(self, event_bus: EventBus, token: str):
        self.event_bus = event_bus
        self.client = Client(token).init()

        self.current_player = None
        self.current_audio = None
        self.current_pos_ms = 0

        event_bus.subscribe("ym_play", self.play_track)
        event_bus.subscribe("ym_pause", self.pause)
        event_bus.subscribe("ym_resume", self.resume)
        event_bus.subscribe("ym_stop", self.stop)

    def play_track(self, data):
        query = data.get("query")
        if not query:
            print("Не указано название трека")
            return

        print("Ищу трек…")

        result = self.client.search(query, type_="track")
        if not result.tracks or not result.tracks.results:
            print("Трек не найден")
            return

        track = result.tracks.results[0]

        os.makedirs("cache", exist_ok=True)
        filepath = f"cache/{track.id}.mp3"

        if not os.path.exists(filepath):
            print("Скачиваю трек…")
            track.download(filepath)

        self.current_audio = AudioSegment.from_mp3(filepath)
        self.current_pos_ms = 0

        self.current_player = _play_with_simpleaudio(self.current_audio)
        print(f"Играет: {track.title} - {track.artists[0].name}")

    def pause(self, data=None):
        if self.current_player and self.current_player.is_playing():
            self.current_player.stop()
            print("Пауза")

    def resume(self, data=None):
        if self.current_audio:
            self.current_player = _play_with_simpleaudio(self.current_audio)
            print("Продолжение проигрывания")

    def stop(self, data=None):
        if self.current_player:
            self.current_player.stop()
            print("Остановлено")
            self.current_player = None

if __name__ == "__main__":
    # Простейший EventBus для теста
    class TestBus:
        def subscribe(self, event, handler):
            self.handler = handler
        def emit(self, event, data=None):
            self.handler(data)

    token = input("Введите токен Яндекс.Музыки: ")
    bus = TestBus()
    ym = YandexMusicModule(bus, token)

    while True:
        cmd = input("Введите команду (play <название>/pause/resume/stop/exit): ")
        if cmd.startswith("play "):
            ym.play_track({"query": cmd[5:]})
        elif cmd == "pause":
            ym.pause()
        elif cmd == "resume":
            ym.resume()
        elif cmd == "stop":
            ym.stop()
        elif cmd == "exit":
            ym.stop()
            break
