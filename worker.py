import os
import time
import pythoncom
from PySide6.QtCore import QObject, Signal
from builders import ConeModelBuilder
from director import ModelDirector

class OptimizationWorker(QObject):
    """Объект-исполнитель для итеративного расчета."""
    
    progress_updated = Signal(int)
    log_message = Signal(str)
    result_ready = Signal(dict)
    finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, params):
        super().__init__()
        self.params = params
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        try:
            pythoncom.CoInitialize()
            builder = ConeModelBuilder()
            director = ModelDirector(builder)
            
            thicknesses = self.params['skin_range']
            str_counts = self.params['str_counts']
            selected_profiles = self.params['profiles']
            
            total_tasks = len(thicknesses) * len(str_counts) * len(selected_profiles)
            if total_tasks == 0:
                self.finished.emit(); return

            current_task_idx = 0
            for t in thicknesses:
                for n in str_counts:
                    for profile in selected_profiles:
                        if not self._is_running:
                            self.log_message.emit("Остановка..."); self.finished.emit(); return

                        current_task_idx += 1
                        config = {
                            "material": self.params['material'],
                            "geometry": self.params['geometry'],
                            "loads": self.params['loads'],
                            "mesh": {"divisions_circular": 40, "divisions_height": 20, "stringers_count": n},
                            "properties": [
                                {"type": "plate", "name": f"Skin_{t}", "thickness": t},
                                {"type": "beam_z", "name": f"Str_{profile['Номер профиля']}", 
                                 "dimensions": {"h": profile["H, мм"], "w_top": profile["B, мм"], "w_bot": profile["B, мм"], 
                                                "t_top": profile["S, мм"], "t_bot": profile["S2, мм"], "t_web": profile["S1, мм"]}}
                            ]
                        }

                        file_name = f"opt_t{t}_n{n}_p{profile['Номер профиля']}.modfem"
                        output_path = os.path.join(os.getcwd(), "models", file_name)
                        
                        # Запуск расчета (Директор вернет макс. напряжение)
                        max_stress = director.construct_and_solve(config, output_path)
                        
                        if max_stress is not None:
                            self.result_ready.emit({
                                "t": t,
                                "n": n,
                                "profile": profile["Номер профиля"],
                                "max_stress": max_stress,
                                "status": "Success"
                            })
                        
                        self.progress_updated.emit(int((current_task_idx / total_tasks) * 100))

            self.finished.emit()
        except Exception as e:
            self.error_occurred.emit(str(e)); self.finished.emit()
        finally:
            pythoncom.CoUninitialize()
