import os
import json
import numpy as np
import traceback
from PySide6.QtCore import QThread, Signal, Qt
from worker import OptimizationWorker
from db_manager import DatabaseManager

class RocketController:
    def __init__(self, view):
        self.view = view
        self.thread = None
        self.worker = None
        self.db_manager = DatabaseManager()
        self.nastran_path = None
        self._init_db_connection()
        
        self.view.run_requested.connect(self.handle_run)
        self.view.stop_requested.connect(self.handle_stop)
        self.view.femap_event_received.connect(self.dispatch_femap_event)
        self._restore_ui_from_checkpoint()

    def _init_db_connection(self):
        try:
            with open("config.json", 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                cfg = config_data.get("database")
                if cfg: self.db_manager.connect_db(cfg)
                self.nastran_path = config_data.get("nastran_path")
        except: pass

    def _restore_ui_from_checkpoint(self):
        if not os.path.exists("checkpoint.json"): return
        try:
            with open("checkpoint.json", "r", encoding='utf-8') as f: p = json.load(f)
            ui = self.view.ui
            g = p.get("geometry", {}); ui.sb_height.setText(str(g.get("height", ""))); ui.sb_d_small.setText(str(g.get("diameter_small", ""))); ui.sb_d_large.setText(str(g.get("diameter_big", "")))
            m = p.get("material", {}); ui.txt_mat_name.setText(m.get("name", "")); ui.sb_mat_e.setText(str(m.get("E", ""))); ui.sb_mat_nu.setText(str(m.get("nu", ""))); ui.sb_mat_density.setText(str(m.get("rho", ""))); ui.sb_mat_sigma.setText(str(m.get("yield", "")))
            ui.sb_load.setText(str(p.get("loads", {}).get("axial_force", "")))
            t_min = p.get("ui_t_min") or (p.get("skin_range")[0] if p.get("skin_range") else "0.5")
            t_max = p.get("ui_t_max") or (p.get("skin_range")[-1] if p.get("skin_range") else "2.0")
            ui.sb_thick_min.setText(str(t_min)); ui.sb_thick_max.setText(str(t_max)); ui.sb_thick_step.setText(str(p.get("ui_t_step", "")))
            
            ui.sb_str_min.setValue(int(p.get("ui_n_min", 40)))
            ui.sb_str_max.setValue(int(p.get("ui_n_max", 80)))
            try: ui.sb_str_step.setValue(int(p.get("ui_n_step", 10)))
            except: pass
            
            ui.sb_elements_between.setValue(int(p.get("elements_between", 2)))
            try: ui.sb_str_along.setValue(int(p.get("elements_along", 20)))
            except: pass
            
            sn = [prof.get("Номер профиля") for prof in p.get("profiles", [])]
            if sn:
                ui.table_profiles.clearSelection()
                for r in range(ui.table_profiles.rowCount()):
                    it = ui.table_profiles.item(r, 0)
                    if it and it.text() in sn: ui.table_profiles.selectRow(r)
            self.update_log("Интерфейс восстановлен из чекпоинта.")
        except Exception as e: print(f"Ошибка восстановления: {e}")

    def dispatch_femap_event(self, event_code):
        if self.worker: self.worker.notify_femap_event(event_code)

    def handle_run(self):
        try:
            ui = self.view.ui
            params = None
            if os.path.exists("checkpoint.json"):
                with open("checkpoint.json", "r", encoding='utf-8') as f: params = json.load(f)
            
            if params is None:
                def get_val(w):
                    try: return float(w.text().strip().replace(",", "."))
                    except: return 0.0
                
                geometry = {"height": get_val(ui.sb_height), "diameter_small": get_val(ui.sb_d_small), "diameter_big": get_val(ui.sb_d_large)}
                material = {"name": ui.txt_mat_name.text(), "E": get_val(ui.sb_mat_e), "nu": get_val(ui.sb_mat_nu), "rho": get_val(ui.sb_mat_density), "yield": get_val(ui.sb_mat_sigma)}
                loads = {"axial_force": get_val(ui.sb_load)}
                
                t_min, t_max, t_step = get_val(ui.sb_thick_min), get_val(ui.sb_thick_max), get_val(ui.sb_thick_step)
                skin_range = np.arange(t_min, t_max + t_step, t_step).tolist()
                
                n_min, n_max, n_step = ui.sb_str_min.value(), ui.sb_str_max.value(), ui.sb_str_step.value()
                str_counts = list(range(n_min, n_max + 1, n_step))
                
                eb = ui.sb_elements_between.value()
                try: ea = ui.sb_str_along.value()
                except: ea = 20
                
                si = ui.table_profiles.selectionModel().selectedRows()
                profiles = [self.view.profiles[item.row()] for item in si] if si else self.view.profiles
                
                params = {"geometry": geometry, "material": material, "loads": loads, "skin_range": skin_range, "str_counts": str_counts, 
                          "profiles": profiles, "elements_between": eb, "elements_along": ea,
                          "ui_t_min": t_min, "ui_t_max": t_max, "ui_t_step": t_step, 
                          "ui_n_min": n_min, "ui_n_max": n_max, "ui_n_step": n_step,
                          "resume_t_idx": 0, "resume_n_idx": 0, "resume_p_idx": 0,
                          "nastran_path": self.nastran_path}

            self.thread = QThread(); self.worker = OptimizationWorker(params); self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run); self.worker.finished.connect(self.thread.quit)
            self.worker.progress_updated.connect(self.view.ui.progressBar.setValue)
            self.worker.log_message.connect(self.update_log)
            self.worker.result_ready.connect(self.handle_result)
            self.view.ui.btn_run.setEnabled(False); self.thread.finished.connect(lambda: self.view.ui.btn_run.setEnabled(True))
            self.thread.start()
        except Exception as e: self.update_log(f"ОШИБКА: {e}"); print(traceback.format_exc())

    def handle_stop(self):
        if self.worker: self.worker.stop(); self.update_log("Остановка. Прогресс сохранен.")

    def update_log(self, message): self.view.ui.log_output.append(message)

    def handle_result(self, d):
        self.db_manager.save_iteration_result(d)
        msg = f"[Прошло {d['difference_time']}, {d['current_idx']}/{d['total_tasks']}] t={d['t']}, n={d['n']}, profile={d['profile']}, StressPl={d['max_stress']:.2e}, Eig={d['eigenvalue']:.4f}"
        self.update_log(msg)
