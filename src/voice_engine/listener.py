import os
import sounddevice as sd
import queue
import json
import time
import logging
from vosk import Model, KaldiRecognizer
from src.core.event_bus import EventBus


class VoiceModule:
    def __init__(self, event_bus: EventBus, model_path=None, log_level=logging.INFO, keyword="астра", pause_threshold=5, listening_pause_threshold=15):
        """
        model_path — путь к модели Vosk (по умолчанию относительный)
        keyword — ключевое слово активации
        pause_threshold — длительность паузы (в секундах) для SLEEP режима
        listening_pause_threshold — длительность паузы для LISTENING режима
        """
        logging.basicConfig(
            level=log_level,
            format="[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S"
        )
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self.pause_threshold = pause_threshold
        self.listening_pause_threshold = listening_pause_threshold
        self.current_pause_threshold = pause_threshold 

        # Путь к модели
        if model_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, "models", "vosk-model-small-ru-0.22")

        if not os.path.exists(model_path):
            self.logger.critical(f"[Listener] Модель не найдена по пути: {model_path}")
            raise FileNotFoundError(f"Модель не найдена по пути: {model_path}")

        self.logger.info(f"[Listener] Загрузка модели речи из: {model_path}")
        self.model = Model(model_path)
        self.samplerate = 16000
        self.recognizer = KaldiRecognizer(self.model, self.samplerate)
        self.q = queue.Queue()
        self.logger.info("[Listener] Модель успешно загружена.")
        self.listening = False

    def set_pause_threshold(self, seconds):
        """Установить порог паузы для текущего режима"""
        self.current_pause_threshold = seconds

    def set_listening_mode(self, is_listening=False):
        """Переключить режим прослушивания"""
        if is_listening:
            self.current_pause_threshold = self.listening_pause_threshold
        else:
            self.current_pause_threshold = self.pause_threshold


    def _callback(self, indata, frames, time_info, status):
        """Обработка поступающих данных с микрофона."""
        if status:
            self.logger.warning(f"[Listener] Аудио статус: {status}")
        self.q.put(bytes(indata))

    def listen(self):
        """
        Слушает микрофон.
        После ключевого слова начинает запись текста
        и автоматически завершает запись после паузы.
        """
        recording = True
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
                self.logger.info(f"[Listener] Начало прослушивания (пауза: {self.current_pause_threshold}с)")

                while True:
                    try:
                        data = self.q.get(timeout=0.1)
                    except queue.Empty:
                        # Проверяем, не истекла ли пауза
                        if recording and (time.time() - last_voice_time > self.current_pause_threshold):
                            self.logger.info("[Listener] Пауза превысила порог, завершение прослушивания")
                            break
                        continue

                    if self.recognizer.AcceptWaveform(data):
                        try:
                            result = json.loads(self.recognizer.Result())
                            text = result.get("text", "").lower()
                        except json.JSONDecodeError:
                            self.logger.error("[Listener] Ошибка декодирования результата распознавания.")
                            continue

                        if not text:
                            continue

                        self.logger.info(f"Распознано: {text}")
                        last_voice_time = time.time()  # обновляем момент последней речи

                        text = text.strip()

                        if recording:
                            recorded_text += " " + text
                 
                return recorded_text.strip()

        except KeyboardInterrupt:
            self.logger.info("[Listener] Прослушивание остановлено пользователем.")
        except Exception as e:
            self.logger.exception(f"[Listener] Ошибка при работе с микрофона: {e}")
        finally:
            self.logger.info("[Listener] Прослушивание завершено")

    def run(self):
        """Запускает модуль и возвращает текст после ключевого слова."""
        return self.listen()