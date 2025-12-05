if model_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, "models", "vosk-model-ru-0.42")

        if not os.path.exists(model_path):
            self.logger.critical(f"Модель не найдена по пути: {model_path}")
            raise FileNotFoundError(f"Модель не найдена по пути: {model_path}")