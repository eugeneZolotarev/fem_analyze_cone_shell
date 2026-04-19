from PySide6.QtWidgets import QWidget, QMainWindow

from ui.ui_main_window import Ui_MainWindow


class RocketApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Инициализация интерфейса
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # --- Дальше идет ваш обычный код ---

        # Настройка таблицы (зебра, выделение строки)
        from PySide6.QtWidgets import QAbstractItemView, QHeaderView
        self.ui.table_profiles.setAlternatingRowColors(True)
        self.ui.table_profiles.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.table_profiles.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = self.ui.table_profiles.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

        # Привязка кнопок
        self.ui.btn_run.clicked.connect(self.start_optimization)

    def start_optimization(self):
        print("Запуск...")