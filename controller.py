import os
import json
import numpy as np
from PySide6.QtCore import QThread, Signal
from worker import OptimizationWorker
from db_manager import DatabaseManager

class RocketController:
    """Контроллер, связывающий View, Worker и Базу Данных."""
    
    def __init__(self, view):
        self.view = view
        self.thread = None
        self.worker = None
        
        # Инициализируем менеджер БД
        self.db_manager = DatabaseManager()
        self._init_db_connection()
        
        # Подписываемся на сигналы
        self.view.run_requested.connect(self.handle_run)
        self.view.stop_requested.connect(self.handle_stop)
        self.view.femap_event_received.connect(self.dispatch_femap_event)

    def _init_db_connection(self):
        """Читает конфиг и подключается к базе данных."""
        try:
            config_path = "config.json"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    db_config = config.get("database")
                    if db_config:
                        success, msg = self.db_manager.connect_db(db_config)
                        if success:
                            self.update_log("База данных: Подключено.")
                        else:
                            self.update_log(f"База данных: Ошибка - {msg}")
        except Exception as e:
            print(f"Ошибка инициализации БД: {e}")

    def dispatch_femap_event(self, event_code):
        if self.worker:
            self.worker.notify_femap_event(event_code)

    def handle_run(self):
        try:
            ui = self.view.ui
            
            # Сбор параметров из UI
            geometry = {"height": ui.sb_height.value(), "diameter_small": ui.sb_d_small.value(), "diameter_big": ui.sb_d_large.value()}
            material = {"name": ui.txt_mat_name.text(), "E": ui.sb_mat_e.value(), "nu": ui.sb_mat_nu.value(), "rho": 7.8e-9}
            loads = {"axial_force": -1000.0}
            
            skin_range = np.arange(ui.sb_thick_min.value(), ui.sb_thick_max.value() + ui.sb_thick_step.value(), ui.sb_thick_step.value()).tolist()
            str_counts = list(range(ui.sb_str_min.value(), ui.sb_str_max.value() + 1, ui.sb_str_step.value()))
            
            selected_profiles = []
            selected_items = ui.table_profiles.selectionModel().selectedRows()
            if selected_items:
                for item in selected_items: selected_profiles.append(self.view.profiles[item.row()])
            else:
                selected_profiles = self.view.profiles

            params = {"geometry": geometry, "material": material, "loads": loads, "skin_range": skin_range, "str_counts": str_counts, "profiles": selected_profiles}

            # Настройка воркера и потока
            self.thread = QThread()
            # ИСПРАВЛЕНИЕ: Передаем только params, как и ожидает конструктор в worker.py
            self.worker = OptimizationWorker(params)
            self.worker.moveToThread(self.thread)
            
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.progress_updated.connect(ui.progressBar.setValue)
            self.worker.log_message.connect(self.update_log)
            
            self.worker.result_ready.connect(self.handle_result)
            
            ui.btn_run.setEnabled(False)
            self.thread.finished.connect(lambda: ui.btn_run.setEnabled(True))
            
            self.thread.start()
            self.update_log("Процесс оптимизации запущен...")

        except Exception as e:
            self.update_log(f"ОШИБКА: {e}")

    def handle_stop(self):
        if self.worker:
            self.worker.stop()
            self.update_log("Остановка...")

    def update_log(self, message):
        self.view.ui.log_output.append(message)

    def handle_result(self, result_data):
        success = self.db_manager.save_iteration_result(result_data)
        if success:
            msg = f"БД: t={result_data['t']}, n={result_data['n']}, Stress={result_data.get('max_stress', 0):.2e}"
            self.update_log(msg)
        else:
            self.update_log("Ошибка при сохранении в БД.")
