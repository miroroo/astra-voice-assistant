import os
import sounddevice as sd
import queue
import json
import time
import logging
from vosk import Model, KaldiRecognizer


class VoiceModule:
    def __init__(self, model_path=None, log_level=logging.INFO, keyword="астра", pause_threshold=5):
        """
        model_path — путь к модели Vosk (по умолчанию относительный)
        keyword — ключевое слово активации
        pause_threshold — длительность паузы (в секундах) для автоостановки
        """
        logging.basicConfig(
            level=log_level,
            format="[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S"
        )
        self.logger = logging.getLogger(__name__)
        self.keyword = keyword
        self.pause_threshold = pause_threshold

        # Путь к модели
        if model_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, "models", "vosk-model-small-ru-0.22")

        if not os.path.exists(model_path):
            self.logger.critical(f"Модель не найдена по пути: {model_path}")
            raise FileNotFoundError(f"Модель не найдена по пути: {model_path}")

        self.logger.info(f"Загрузка модели речи из: {model_path}")
        self.model = Model(model_path)
        self.samplerate = 16000
        self.recognizer = KaldiRecognizer(self.model, self.samplerate)
        self.q = queue.Queue()
        self.logger.info("Модель успешно загружена.")

    def _callback(self, indata, frames, time_info, status):
        """Обработка поступающих данных с микрофона."""
        if status:
            self.logger.warning(f"Аудио статус: {status}")
        self.q.put(bytes(indata))

    def listen(self):
        """
        Слушает микрофон.
        После ключевого слова начинает запись текста
        и автоматически завершает запись после паузы.
        """
        recording = False
        recorded_text = ""
        last_voice_time = time.time()

        try:
            with sd.RawInputStream(
                samplerate=self.samplerate,
                blocksize=8000,
                dtype='int16',
                channels=1,
                callback=self._callback
            ):
                self.logger.info("Прослушивание микрофона запущено...")

                while True:
                    try:
                        data = self.q.get(timeout=0.1)
                    except queue.Empty:
                        # Проверяем, не истекла ли пауза
                        if recording and (time.time() - last_voice_time > self.pause_threshold):
                            self.logger.info(f"Пауза {self.pause_threshold} с — запись завершена.")
                            break
                        continue

                    if self.recognizer.AcceptWaveform(data):
                        try:
                            result = json.loads(self.recognizer.Result())
                            text = result.get("text", "").lower()
                        except json.JSONDecodeError:
                            self.logger.error("Ошибка декодирования результата распознавания.")
                            continue

                        if not text:
                            continue

                        self.logger.info(f"Распознано: {text}")
                        last_voice_time = time.time()  # обновляем момент последней речи

                        if self.keyword in text and not recording:
                            recording = True
                            self.logger.info(f"Ключевое слово '{self.keyword}' найдено. Начинаем запись...")
                            # Убираем само ключевое слово из текста
                            text = text.replace(self.keyword, "").strip()

                        if recording:
                            recorded_text += " " + text

        except KeyboardInterrupt:
            self.logger.info("Прослушивание остановлено пользователем.")
        except Exception as e:
            self.logger.exception(f"Ошибка при работе с микрофоном: {e}")

        return recorded_text.strip()

    def run(self):
        """Запускает модуль и возвращает текст после ключевого слова."""
        return self.listen()


if __name__ == "__main__":
    vm = VoiceModule(pause_threshold=3)
    text_after_keyword = vm.run()
    print("Текст после ключевого слова:", text_after_keyword)
