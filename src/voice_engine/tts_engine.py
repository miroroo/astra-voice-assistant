import pyttsx3

class TTSModule:
    # создаём движок один раз на весь класс / процесс
    engine = pyttsx3.init()
    
    def __init__(self, text, rate = 180, volume=1.0, lang = 'ru', gender = 'female'):
        """
        Инициализация объекта класса.
        
        Параметры:
        text : str        - текст для озвучивания (обязательный)
        rate : int        - скорость речи (слов в минуту), по умолчанию 180
        volume : float    - громкость речи (0.0 - 1.0), по умолчанию 1.0
        lang : str        - язык речи, например "ru" или "en"
        gender : str      - пол голоса, "male" или "female"
        """
    
        self.text = text
        self.rate = rate
        self.volume = volume
        self.lang = lang
        self.gender = gender
        self.voice = None # Переменная для выбранного голоса (объект pyttsx3.Voice)
        
        # настройка движка
        self.engine.setProperty('rate', self.rate)
        self.engine.setProperty('volume', self.volume)
        
        # Выбираем первый подходящий голос по языку и полу
        for v in self.engine.getProperty('voices'):
            # v.languages — список строк, например ["en_US"]
            if lang in v.languages[0] and gender in v.name.lower():
                self.voice = v
                self.engine.setProperty('voice', v.id)
                break
        # Если подходящего голоса не нашли — pyttsx3 возьмёт голос по умолчанию

    def say(self):
        """
        Озвучивает текст, сохранённый в self.text.
        """
        self.engine.say(self.text)
        # Запускаем синтез речи и ждём окончания
        self.engine.runAndWait()
        # очищаем очередь, чтобы следующий вызов сработал
        self.engine.stop()


if __name__ == "__main__":
    tts = TTSModule("Привет, я голос Астры!")
    tts.say()
