import os
import time
import math
import pythoncom
from PySide6.QtCore import QObject, Signal
from builders import ConeModelBuilder
from director import ModelDirector

class OptimizationWorker(QObject):
    """Объект-исполнитель с исправленной передачей данных."""
    
    progress_updated = Signal(int)
    log_message = Signal(str)
    result_ready = Signal(dict)
    finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, params):
        super().__init__()
        self.params = params
        self._is_running = True
        self.builder = None

    def stop(self): self._is_running = False

    def notify_femap_event(self, event_code):
        if event_code == 11 and self.builder:
            self.builder.notify_analysis_finished()

    def run(self):
        try:
            pythoncom.CoInitialize()
            self.builder = ConeModelBuilder()
            director = ModelDirector(self.builder)
            
            thicknesses = self.params['skin_range']
            str_counts = self.params['str_counts']
            selected_profiles = self.params['profiles']
            multiplier = self.params.get('elements_between', 2)
            div_height = int(self.params.get('elements_along', 20))
            
            geom = self.params['geometry']
            material = self.params['material']
            rho = material.get('rho', 0.0)
            
            H_m, D_m, d_m = geom['height']/1000, geom['diameter_big']/1000, geom['diameter_small']/1000
            L_m = math.sqrt(H_m**2 + ((D_m - d_m)/2)**2)
            shell_area = math.pi * (D_m/2 + d_m/2) * L_m
            
            total_tasks = len(thicknesses) * len(str_counts) * len(selected_profiles)
            if total_tasks == 0: self.finished.emit(); return

            print(f"--- ЗАПУСК ЦИКЛА ВОРКЕРА ---")
            current_task_idx = 0
            
            for t in thicknesses:
                shell_mass = shell_area * (t/1000) * rho
                for n in str_counts:
                    div_circular = n * multiplier
                    print(f"DEBUG WORKER: Пересчет сетки: n={n}, Circ={div_circular}, Height={div_height}")
                    
                    for profile in selected_profiles:
                        if not self._is_running:
                            self.log_message.emit("Процесс прерван."); self.finished.emit(); return

                        current_task_idx += 1
                        config = {
                            "material": material, "geometry": geom, "loads": self.params['loads'],
                            "mesh": {"divisions_circular": div_circular, "divisions_height": div_height, "stringers_count": n},
                            "properties": [
                                {"type": "plate", "name": f"Skin_{t}", "thickness": t},
                                {"type": "beam_z", "name": f"Str_{profile['Номер профиля']}", 
                                 "dimensions": {"h": profile["H, мм"], "w_top": profile["B, мм"], "w_bot": profile["B, мм"], 
                                                "t_top": profile["S, мм"], "t_bot": profile["S2, мм"], "t_web": profile["S1, мм"]}}
                            ]
                        }

                        output_path = os.path.join(os.getcwd(), "models", f"opt_{current_task_idx}.modfem")
                        
                        # ВАЖНО: Директор возвращает СЛОВАРЬ {'max_stress': ..., 'eigenvalue': ...}
                        calc_result = director.construct_and_solve(config, output_path)
                        
                        if calc_result is not None:
                            # Расчет массы
                            m_1m = (profile.get("Теоретическая масса 1 м, кг") or 
                                    profile.get("Теоретическая mass 1 м, кг") or {}).get("Алюминиевый сплав", 0.0)
                            total_mass = shell_mass + (n * L_m * m_1m)

                            # ОТПРАВКА ДАННЫХ (Распаковываем словарь из директора)
                            self.result_ready.emit({
                                "t": t, "n": n, "profile": profile["Номер профиля"],
                                "max_stress": calc_result.get("max_stress", 0.0),
                                "eigenvalue": calc_result.get("eigenvalue", 0.0),
                                "mass": total_mass,
                                "status": "Success"
                            })
                        
                        self.progress_updated.emit(int((current_task_idx / total_tasks) * 100))

            self.finished.emit()
        except Exception as e:
            print(f"КРИТИЧЕСКАЯ ОШИБКА ВОРКЕРА: {e}")
            print(traceback.format_exc())
            self.error_occurred.emit(str(e)); self.finished.emit()
        finally: pythoncom.CoUninitialize()
