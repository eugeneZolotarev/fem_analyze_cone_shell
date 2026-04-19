from PySide6.QtWidgets import QWidget, QMainWindow, QAbstractItemView, QHeaderView
from ui.ui_main_window import Ui_MainWindow

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class RocketApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Инициализация интерфейса
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # --- Настройка Matplotlib Backend ---
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        # Добавляем холст в заранее созданный layout_plot
        self.ui.layout_plot.addWidget(self.canvas)

        # --- Настройка таблицы ---
        self.ui.table_profiles.setAlternatingRowColors(True)
        self.ui.table_profiles.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.table_profiles.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = self.ui.table_profiles.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

        # Привязка кнопок
        self.ui.btn_run.clicked.connect(self.start_optimization)

        # Пример отрисовки при запуске с оригинальными параметрами
        self.draw_section(h=1.2, b_c=67.55, c_c=1.0, b_nc=22.97, title="Сечение по умолчанию")

    def draw_section(self, h, b_c, c_c, b_nc, title):
        """Отрисовка сечения стрингера и обшивки в layout_plot (прежняя версия)."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # --- Расчет координат для отрисовки ---
        skin_width = 80
        skin_x = [-skin_width / 2, skin_width / 2]
        skin_y = [-h / 2, -h / 2]

        lower_flange_x = [0, b_nc]
        lower_flange_y = [c_c / 2, c_c / 2]

        web_x = [0, 0]
        web_y = [c_c / 2, c_c / 2 + b_c]

        upper_flange_x = [-b_nc, 0]
        upper_flange_y = [c_c / 2 + b_c, c_c / 2 + b_c]

        # --- Расчет центра тяжести ---
        A1, A2, A3 = b_nc * c_c, b_c * c_c, b_nc * c_c
        A_total = A1 + A2 + A3
        x1, x2, x3 = b_nc / 2, 0, -b_nc / 2
        y1, y2, y3 = c_c / 2, c_c + b_c / 2, c_c + b_c - c_c / 2

        x_c = (A1 * x1 + A2 * x2 + A3 * x3) / A_total
        y_c = (A1 * y1 + A2 * y2 + A3 * y3) / A_total

        # --- Построение графика ---
        scale_lw = 4

        # Рисуем обшивку (серым)
        ax.plot(skin_x, skin_y, color="gray", lw=h * scale_lw, solid_capstyle="butt", label=f"Обшивка (h={h} мм)")

        # Рисуем Z-стрингер (синим)
        ax.plot(lower_flange_x, lower_flange_y, color="blue", lw=c_c * scale_lw, solid_capstyle="butt", label=f"Z-стрингер ($c_c$={c_c} мм)")
        ax.plot(web_x, web_y, color="blue", lw=c_c * scale_lw, solid_capstyle="butt")
        ax.plot(upper_flange_x, upper_flange_y, color="blue", lw=c_c * scale_lw, solid_capstyle="butt")

        # Отмечаем центр тяжести
        ax.plot(x_c, y_c, "ro", markersize=8, label=f"Центр масс ЦТ ({x_c:.1f}, {y_c:.1f})")

        # Настройка осей
        ax.set_aspect("equal")
        ax.set_title(title)
        ax.set_xlabel("Ширина сечения, мм")
        ax.set_ylabel("Высота сечения, мм")

        # Выноски
        ax.annotate(f"$b_c$={b_c} мм", xy=(2, y2), xytext=(15, y2), arrowprops=dict(arrowstyle="->"))
        ax.annotate(f"$b_{{nc}}$={b_nc} мм", xy=(x3, y3 - 2), xytext=(x3, y3 - 10), arrowprops=dict(arrowstyle="->"), ha="center", va="top")
        ax.annotate(f"$b_{{nc}}$={b_nc} мм", xy=(x1, y1 + 2), xytext=(x1, y1 + 10), arrowprops=dict(arrowstyle="->"), ha="center", va="bottom")

        ax.grid(True, linestyle="--", alpha=0.7)
        ax.legend(loc="upper right")

        # Обновляем холст в GUI
        self.canvas.draw()

    def start_optimization(self):
        print("Запуск оптимизации...")
