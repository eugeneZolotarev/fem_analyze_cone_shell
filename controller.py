import os
import json
import numpy as np
import traceback
from PySide6.QtCore import QThread, Signal
from worker import OptimizationWorker
from db_manager import DatabaseManager

class RocketController:
    """Контроллер с детальным логированием и корректной передачей данных."""
    
    def __init__(self, view):
        self.view = view
        self.thread = None
        self.worker = None
        self.db_manager = DatabaseManager()
        self._init_db_connection()
        
        self.view.run_requested.connect(self.handle_run)
        self.view.stop_requested.connect(self.handle_stop)
        self.view.femap_event_received.connect(self.dispatch_femap_event)

    def _init_db_connection(self):
        try:
            config_path = "config.json"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    db_config = config.get("database")
                    if db_config:
                        success, msg = self.db_manager.connect_db(db_config)
                        self.update_log(f"База данных: {msg}")
        except: pass

    def dispatch_femap_event(self, event_code):
        if self.worker: self.worker.notify_femap_event(event_code)

    def handle_run(self):
        """Сбор параметров из UI и запуск потока с подробным выводом."""
        try:
            ui = self.view.ui
            def get_val(widget):
                try: 
                    t = widget.text().strip().replace(",", ".")
                    return float(t) if t else 0.0
                except: return 0.0

            # 1. Сбор параметров
            geometry = {"height": get_val(ui.sb_height), "diameter_small": get_val(ui.sb_d_small), "diameter_big": get_val(ui.sb_d_large)}
            material = {"name": ui.txt_mat_name.text(), "E": get_val(ui.sb_mat_e), "nu": get_val(ui.sb_mat_nu), "rho": get_val(ui.sb_mat_density)}
            loads = {"axial_force": get_val(ui.sb_load)} 
            
            t_min, t_max, t_step = get_val(ui.sb_thick_min), get_val(ui.sb_thick_max), get_val(ui.sb_thick_step)
            skin_range = np.arange(t_min, t_max + t_step, t_step).tolist()
            
            n_min, n_max = ui.sb_str_min.value(), ui.sb_str_max.value()
            str_counts = list(range(n_min, n_max + 1, 10)) 
            
            try: elements_along = ui.sb_str_along.value()
            except: elements_along = 20
            elements_between = ui.sb_elements_between.value()

            selected_profiles = []
            selected_items = ui.table_profiles.selectionModel().selectedRows()
            if selected_items:
                for item in selected_items: selected_profiles.append(self.view.profiles[item.row()])
            else: selected_profiles = self.view.profiles

            total_tasks = len(skin_range) * len(str_counts) * len(selected_profiles)

            # ПОДРОБНОЕ ЛОГИРОВАНИЕ В КОНСОЛЬ
            print("\n" + "="*50)
            print("ПАРАМЕТРЫ ОПТИМИЗАЦИИ:")
            print(f"  Геометрия: H={geometry['height']}, d={geometry['diameter_small']}, D={geometry['diameter_big']}")
            print(f"  Материал: {material['name']} (E={material['E']}, rho={material['rho']})")
            print(f"  Нагрузка: {loads['axial_force']} H")
            print(f"  Сетка: Вдоль={elements_along}, Между={elements_between}")
            print(f"  Диапазоны: t=[{t_min}:{t_max}], n=[{n_min}:{n_max}]")
            print(f"  Всего расчетных случаев: {total_tasks}")
            print("="*50 + "\n")

            params = {"geometry": geometry, "material": material, "loads": loads, "skin_range": skin_range, "str_counts": str_counts, 
                      "profiles": selected_profiles, "elements_between": elements_between, "elements_along": elements_along}

            self.thread = QThread(); self.worker = OptimizationWorker(params); self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run); self.worker.finished.connect(self.thread.quit)
            self.worker.progress_updated.connect(ui.progressBar.setValue); self.worker.log_message.connect(self.update_log); self.worker.result_ready.connect(self.handle_result)
            ui.btn_run.setEnabled(False); self.thread.finished.connect(lambda: ui.btn_run.setEnabled(True))
            
            self.thread.start()
            self.update_log(f"Процесс запущен. Всего итераций: {total_tasks}")

        except Exception as e:
            self.update_log(f"ОШИБКА: {e}")
            print(traceback.format_exc())

    def handle_stop(self):
        if self.worker: self.worker.stop(); self.update_log("Остановка...")

    def update_log(self, message): self.view.ui.log_output.append(message)

    def handle_result(self, d):
        """Запись в БД и детальный лог в интерфейс."""
        success = self.db_manager.save_iteration_result(d)
        t, n, m, s, e = d['t'], d['n'], d.get('mass', 0.0), d.get('max_stress', 0.0), d.get('eigenvalue', 0.0)
        
        status_db = "OK" if success else "FAIL"
        msg = f"Итерация: t={t}, n={n}, Mass={m:.2f}кг, Eig={e:.4f}, Stress={s:.2e} (БД: {status_db})"
        self.update_log(msg)
        print(f"Результат записан: {msg}")
