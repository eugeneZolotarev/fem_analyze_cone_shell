from PySide6.QtWidgets import QWidget, QMainWindow, QAbstractItemView, QHeaderView, QLabel, QTableWidgetItem
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from ui.ui_main_window import Ui_MainWindow

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import os
import json

class RocketApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Инициализация интерфейса
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # --- Состояние графической области ---
        self.canvas = None
        self.figure = Figure(figsize=(8, 8), dpi=100)
        self.profiles = []
        
        # 1. Создаем виджет для отображения статичного чертежа x004.jpg
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        
        img_path = "ui/x004.jpg"
        if not os.path.exists(img_path):
            img_path = "x004.jpg"
            
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            self.image_label.setPixmap(pixmap.scaled(700, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.image_label.setText(f"Файл чертежа {img_path} не найден")

        self.ui.layout_plot.addWidget(self.image_label)

        # --- Настройка таблицы ---
        self.ui.table_profiles.setAlternatingRowColors(True)
        self.ui.table_profiles.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.table_profiles.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = self.ui.table_profiles.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

        # Загрузка данных из профилей
        self.load_profiles()

        # Привязка событий
        self.ui.btn_run.clicked.connect(self.start_optimization)
        self.ui.table_profiles.itemSelectionChanged.connect(self.on_profile_selected)

    def load_profiles(self):
        """Загружает список профилей из JSON в таблицу."""
        try:
            # Путь к файлу
            json_path = "profiles.json"
            if not os.path.exists(json_path):
                print("Файл profiles.json не найден")
                return

            with open(json_path, "r", encoding="utf-8") as f:
                self.profiles = json.load(f)
            
            if not self.profiles:
                return

            # Заголовки (только алюминий)
            headers = ["Номер", "H", "B", "S", "S1", "S2", "S, см²", "m (Al), кг"]
            self.ui.table_profiles.setColumnCount(len(headers))
            self.ui.table_profiles.setHorizontalHeaderLabels(headers)
            self.ui.table_profiles.setRowCount(len(self.profiles))
            
            for row, p in enumerate(self.profiles):
                # Формируем список значений для строки
                data = [
                    p.get("Номер профиля"),
                    p.get("H, мм"),
                    p.get("B, мм"),
                    p.get("S, мм"),
                    p.get("S1, мм"),
                    p.get("S2, мм"),
                    p.get("Площадь сечения, см2")
                ]
                # Оставляем только алюминий
                mass_info = p.get("Теоретическая mass 1 м, кг", {})
                if not mass_info: # Проверка на опечатку в ключе (в JSON может быть "масса")
                    mass_info = p.get("Теоретическая масса 1 м, кг", {})
                
                data.append(mass_info.get("Алюминиевый сплав"))

                for col, value in enumerate(data):
                    item = QTableWidgetItem(str(value) if value is not None else "-")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.ui.table_profiles.setItem(row, col, item)
            
            print(f"Загружено профилей: {len(self.profiles)}")
                    
        except Exception as e:
            print(f"Ошибка загрузки профилей: {e}")

    def on_profile_selected(self):
        """Обработка выбора профиля в таблице."""
        selected_rows = self.ui.table_profiles.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        p = self.profiles[row]
        
        # Обновляем чертеж на основе данных выбранного профиля
        # Сопоставление имен: h_skin (толщина обшивки), b_c (H), c_c (S1), b_nc (B)
        self.draw_section(
            h=1.5, # Временное значение толщины обшивки
            b_c=float(p.get("H, мм", 0)), 
            c_c=float(p.get("S1, мм", 0)), 
            b_nc=float(p.get("B, мм", 0)),
            title=f"Профиль №{p.get('Номер профиля')}"
        )

    def draw_section(self, h, b_c, c_c, b_nc, title):
        """Скрывает чертеж и отображает интерактивный график Matplotlib."""
        self.image_label.hide()
        
        if self.canvas is None:
            self.canvas = FigureCanvas(self.figure)
            self.ui.layout_plot.addWidget(self.canvas)
        
        self.canvas.show()

        # Отрисовка
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        skin_width = b_nc * 3
        skin_x = [-skin_width / 2, skin_width / 2]
        skin_y = [-h / 2, -h / 2]

        lower_flange_x, lower_flange_y = [0, b_nc], [c_c / 2, c_c / 2]
        web_x, web_y = [0, 0], [c_c / 2, c_c / 2 + b_c]
        upper_flange_x, upper_flange_y = [-b_nc, 0], [c_c / 2 + b_c, c_c / 2 + b_c]

        scale_lw = 4
        ax.plot(skin_x, skin_y, color="gray", lw=h * scale_lw, solid_capstyle="butt", label=f"Обшивка")
        ax.plot(lower_flange_x, lower_flange_y, color="blue", lw=c_c * scale_lw, solid_capstyle="butt", label="Z-стрингер")
        ax.plot(web_x, web_y, color="blue", lw=c_c * scale_lw, solid_capstyle="butt")
        ax.plot(upper_flange_x, upper_flange_y, color="blue", lw=c_c * scale_lw, solid_capstyle="butt")
        
        ax.set_aspect("equal")
        ax.set_title(title)
        ax.set_xlabel("Ширина, мм")
        ax.set_ylabel("Высота, мм")
        ax.grid(True, linestyle="--", alpha=0.7)
        ax.legend(loc="upper right", fontsize='small')

        self.canvas.draw()

    def start_optimization(self):
        print("Запуск оптимизации...")
