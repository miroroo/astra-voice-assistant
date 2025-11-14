import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class TextWindow(QWidget):

    """
    Полупрозрачное окно поверх всех окон, отображающее текст.

    Текст можно обновлять из любого модуля проекта
    через метод update_text().

    """

    def __init__(self):
        super().__init__()

        # Настройки окна
        self.setWindowTitle("Astra Text")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.8)

        self.setGeometry(100, 100, 500, 200)

                # Полупрозрачная белая подложка
        self.setStyleSheet("""
            background-color: rgba(255, 255, 255, 160);
            border-radius: 15px;
        """)


        # Элемент текста
        self.label = QLabel("—")
        self.label.setFont(QFont("Arial", 18))
        self.label.setStyleSheet("color: black;")

        # Верстка
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    # Метод для обновления текста извне
    def update_text(self, text: str):
        self.label.setText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TextWindow()
    win.update_text("привет, Астра!")
    win.show()
    sys.exit(app.exec())