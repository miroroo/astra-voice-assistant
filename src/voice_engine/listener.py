import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer


class VoiceModule:
    def __init__(self, model_path=r"C:\Projects\voice_assistant\astra-voice-assistant\src\voice_engine\models\vosk-model-small-ru-0.22"): 
        """Инициализация модели, микрофона и параметров."""
        print("Загрузка модели речи...")
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.q = queue.Queue()
        self.samplerate = 16000
        self.keyword = "астра"
        print("Модель загружена. Скажите 'Астра', чтобы активировать...")

    def _callback(self, indata, frames, time, status):
        """Функция обратного вызова, которая срабатывает при поступлении данных с микрофона."""
        if status:
            print(status)
        self.q.put(bytes(indata))

    def listen(self):
        """Непрерывное прослушивание микрофона и распознавание ключевого слова."""
        try:
            with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, dtype='int16',
                                   channels=1, callback=self._callback):
                print("Слушаю микрофон...")

                while True:
                    data = self.q.get()
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "").lower()

                        if text:
                            print("Распознано:", text)

                        if self.keyword in text:
                            print("Ключевое слово распознано!")
                            break

        except KeyboardInterrupt:
            print("\nОстановка прослушивания пользователем.")
        except Exception as e:
            print("Ошибка при работе с микрофоном:", e)

    def run(self):
        """Основной запуск модуля."""
        self.listen()


if __name__ == "__main__":
    vm = VoiceModule()
    vm.run()