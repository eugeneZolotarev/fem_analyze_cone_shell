import os
import json
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import RocketApp
from controller import RocketController

# run_automation больше не нужна в этом файле, так как логика переехала в Worker

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Инициализируем Вид (Окно)
    window = RocketApp()
    
    # Инициализируем Контроллер и связываем его с окном
    # Сессия Femap теперь будет создана внутри потока воркера при запуске
    controller = RocketController(window)
    
    window.show()
    sys.exit(app.exec())
