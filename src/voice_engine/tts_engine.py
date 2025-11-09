import pyttsx3

class TTSModule:
    def __init__(self, rate=180, volume=1.0, lang='ru', gender='female'):
        """
        Инициализация объекта класса.
        
        Параметры:
        rate : int        - скорость речи (слов в минуту), по умолчанию 180
        volume : float    - громкость речи (0.0 - 1.0), по умолчанию 1.0
        lang : str        - язык речи, например "ru" или "en"
        gender : str      - пол голоса, "male" или "female"
        """
        self.rate = rate
        self.volume = volume
        self.lang = lang
        self.gender = gender
        self.voice_id = None

        # при инициализации просто запоминаем параметры — без запуска движка
        self._init_voice()

    def _init_voice(self):
        """Отдельный метод для выбора подходящего голоса."""
        engine = pyttsx3.init()
        engine.setProperty('rate', self.rate)
        engine.setProperty('volume', self.volume)

        for v in engine.getProperty('voices'):
            if self.lang in v.languages[0] and self.gender in v.name.lower():
                self.voice_id = v.id
                break
        engine.stop()

    def say(self, text):
        """
        Озвучивает переданный текст.
        Пересоздаёт движок каждый раз (надёжно работает на Windows).
        """
        engine = pyttsx3.init()
        engine.setProperty('rate', self.rate)
        engine.setProperty('volume', self.volume)
        if self.voice_id:
            engine.setProperty('voice', self.voice_id)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        del engine  # гарантируем очистку ресурсов


if __name__ == "__main__":
    tts = TTSModule()
    tts.say("Привет, я голос Астры!")
    tts.say("Привет, это снова я!")