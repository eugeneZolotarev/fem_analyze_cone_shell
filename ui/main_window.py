from PySide6.QtWidgets import QWidget, QMainWindow, QAbstractItemView, QHeaderView, QTableWidgetItem
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

        # --- Настройка Matplotlib (Белый фон, без желтизны) ---
        self.figure = Figure(figsize=(8, 8), dpi=100, facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        self.ui.layout_plot.addWidget(self.canvas)
        
        self.profiles = []
        
        # --- Настройка таблицы ---
        self.ui.table_profiles.setAlternatingRowColors(True)
        self.ui.table_profiles.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.table_profiles.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = self.ui.table_profiles.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

        # 1. Показываем начальную схему x004.jpg
        self.show_initial_schema()

        # 2. Загружаем данные
        self.load_profiles()

        # Привязка событий
        self.ui.btn_run.clicked.connect(self.start_optimization)
        self.ui.table_profiles.itemSelectionChanged.connect(self.on_profile_selected)

    def show_initial_schema(self):
        """Загружает и отображает x004.jpg на чисто белом фоне."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('white') # Белый фон осей
        
        img_path = "ui/x004.jpg"
        if not os.path.exists(img_path):
            img_path = "x004.jpg"
            
        if os.path.exists(img_path):
            try:
                import matplotlib.image as mpimg
                img = mpimg.imread(img_path)
                # cmap='gray' предотвращает появление ложных цветов (желтого/зеленого)
                ax.imshow(img, cmap='gray')
                ax.set_title("Справочная схема Z-профиля", pad=10, color='black')
            except Exception as e:
                ax.text(0.5, 0.5, f"Ошибка загрузки:\n{e}", ha='center', va='center')
        else:
            ax.text(0.5, 0.5, "Файл x004.jpg не найден", ha='center', va='center')

        ax.axis('off')
        self.figure.tight_layout()
        self.canvas.draw()

    def load_profiles(self):
        """Загружает список профилей из JSON в таблицу."""
        try:
            json_path = "profiles.json"
            if not os.path.exists(json_path): return

            with open(json_path, "r", encoding="utf-8") as f:
                self.profiles = json.load(f)
            
            if not self.profiles: return

            headers = ["Номер", "H", "B", "S", "S1", "S2", "S, см²", "m (Al), кг"]
            self.ui.table_profiles.setColumnCount(len(headers))
            self.ui.table_profiles.setHorizontalHeaderLabels(headers)
            self.ui.table_profiles.setRowCount(len(self.profiles))
            
            for row, p in enumerate(self.profiles):
                data = [
                    p.get("Номер профиля"), p.get("H, мм"), p.get("B, мм"),
                    p.get("S, мм"), p.get("S1, мм"), p.get("S2, мм"),
                    p.get("Площадь сечения, см2")
                ]
                mass_info = p.get("Теоретическая масса 1 м, кг") or p.get("Теоретическая mass 1 м, кг") or {}
                data.append(mass_info.get("Алюминиевый сплав"))

                for col, value in enumerate(data):
                    item = QTableWidgetItem(str(value) if value is not None else "-")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.ui.table_profiles.setItem(row, col, item)
                    
        except Exception as e:
            print(f"Ошибка загрузки профилей: {e}")

    def on_profile_selected(self):
        """Обработка выбора профиля в таблице."""
        selected_rows = self.ui.table_profiles.selectionModel().selectedRows()
        if not selected_rows: return
            
        row = selected_rows[0].row()
        p = self.profiles[row]
        
        self.draw_section(
            h=1.5,
            b_c=float(p.get("H, мм", 0)), 
            c_c=float(p.get("S1, мм", 0)), 
            b_nc=float(p.get("B, мм", 0)),
            title=f"Профиль №{p.get('Номер профиля')}"
        )

    def draw_section(self, h, b_c, c_c, b_nc, title):
        """Рисует интерактивное сечение на чисто белом фоне."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('white')

        # Расчет координат
        skin_width = b_nc * 3
        skin_x = [-skin_width / 2, skin_width / 2]
        skin_y = [-h / 2, -h / 2]

        lower_flange_x, lower_flange_y = [0, b_nc], [c_c / 2, c_c / 2]
        web_x, web_y = [0, 0], [c_c / 2, c_c / 2 + b_c]
        upper_flange_x, upper_flange_y = [-b_nc, 0], [c_c / 2 + b_c, c_c / 2 + b_c]

        A1, A2, A3 = b_nc * c_c, b_c * c_c, b_nc * c_c
        A_total = A1 + A2 + A3
        x_c = (A1 * (b_nc/2) + A2 * 0 + A3 * (-b_nc/2)) / A_total
        y_c = (A1 * (c_c/2) + A2 * (c_c + b_c/2) + A3 * (c_c + b_c - c_c/2)) / A_total

        scale_lw = 4
        ax.plot(skin_x, skin_y, color="gray", lw=h * scale_lw, solid_capstyle="butt", label=f"Обшивка")
        ax.plot(lower_flange_x, lower_flange_y, color="blue", lw=c_c * scale_lw, solid_capstyle="butt", label="Z-стрингер")
        ax.plot(web_x, web_y, color="blue", lw=c_c * scale_lw, solid_capstyle="butt")
        ax.plot(upper_flange_x, upper_flange_y, color="blue", lw=c_c * scale_lw, solid_capstyle="butt")
        ax.plot(x_c, y_c, "ro", markersize=8, label=f"ЦТ")

        ax.set_aspect("equal")
        ax.set_title(title, color='black')
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.legend(loc="upper right", fontsize='small')

        self.figure.tight_layout()
        self.canvas.draw()

    def start_optimization(self):
        print("Запуск оптимизации...")
