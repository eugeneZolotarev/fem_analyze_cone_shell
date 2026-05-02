import time
import pythoncom
import traceback
from PySide6.QtCore import QThread, Signal
from builders import ConeModelBuilder
from director import OptimizationDirector

class OptimizationWorker(QThread):
    progress_updated = Signal(int)
    result_ready = Signal(dict)
    finished = Signal()
    error_occurred = Signal(str)
    log_message = Signal(str)

    def __init__(self, params):
        super().__init__()
        self.params = params
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        pythoncom.CoInitialize()
        try:
            builder = ConeModelBuilder(params=self.params)
            director = OptimizationDirector(builder)
            
            stringer_counts = self.params.get("str_counts", [])
            raw_profiles = self.params.get("profiles", [])
            total_tasks = len(stringer_counts) * len(raw_profiles)
            
            self.log_message.emit(f"Запуск оптимизации: {total_tasks} вариантов.")
            
            current_idx = 0
            for s_idx, s_count in enumerate(stringer_counts):
                for p_idx, raw_profile in enumerate(raw_profiles):
                    if not self._is_running: break
                    
                    current_idx += 1
                    start_time = time.time()
                    
                    # Преобразуем формат профиля из JSON (с русскими ключами) в формат для Билдера
                    p_name = raw_profile.get("Номер профиля", "Unknown")
                    profile_formatted = {
                        "name": f"Profile_{p_name}",
                        "type": "beam_z",
                        "dimensions": {
                            "h": float(raw_profile["H, мм"]),
                            "w_bot": float(raw_profile["B, мм"]),
                            "w_top": float(raw_profile["B, мм"]), # Предполагаем равные полки
                            "t_bot": float(raw_profile["S, мм"]),
                            "t_web": float(raw_profile["S1, мм"]),
                            "t_top": float(raw_profile["S2, мм"])
                        }
                    }

                    iter_params = {
                        "geometry": self.params["geometry"].copy(),
                        "material": self.params["material"].copy(),
                        "loads": self.params["loads"].copy(),
                        "mesh": {
                            "divisions_circular": s_count * self.params["elements_between"],
                            "divisions_height": self.params["elements_along"]
                        },
                        "plate_prop": {
                            "name": "Shell", "type": "plate", "thickness": self.params["ui_t_min"]
                        },
                        "beam_prop": profile_formatted,
                        "optimization": {
                            "t_min": self.params["ui_t_min"],
                            "t_max": self.params["ui_t_max"]
                        }
                    }
                    iter_params["geometry"]["stringer_count"] = s_count

                    self.log_message.emit(f"Расчет {current_idx}/{total_tasks}: N={s_count}, Prof={p_name}")
                    
                    res = director.construct_and_solve(iter_params)
                    
                    if res:
                        t_opt = res.get("optimized_thickness", 0.0)
                        sigma_y = float(self.params["material"]["yield"])
                        plate_sf = sigma_y / res["max_stress"] if res["max_stress"] > 0 else 0
                        
                        E = float(self.params["material"]["E"])
                        d = profile_formatted["dimensions"]
                        sigma_cr_flange = 0.46 * E * (d["t_top"] / d["w_top"])**2
                        
                        beam_max = res["beam_max_stress"]
                        flange_buckling_sf = min(sigma_cr_flange / beam_max, sigma_y / beam_max) if beam_max > 0 else 0

                        end_time = time.time()
                        
                        result_data = {
                            "current_idx": current_idx,
                            "total_tasks": total_tasks,
                            "t": t_opt,
                            "n": s_count,
                            "profile": p_name,
                            "max_stress": res["max_stress"],
                            "beam_max_stress": res["beam_max_stress"],
                            "eigenvalue": res["eigenvalue"],
                            "plate_sf": plate_sf,
                            "flange_buckling_sf": flange_buckling_sf,
                            "difference_time": f"{int(end_time - start_time)}s",
                            "skin_thickness": t_opt,
                            "stringer_count": s_count,
                            "profile_name": p_name
                        }
                        self.result_ready.emit(result_data)
                    
                    self.progress_updated.emit(int((current_idx / total_tasks) * 100))
                    
            self.finished.emit()
            
        except Exception as e:
            self.log_message.emit(f"Критическая ошибка: {e}")
            self.error_occurred.emit(str(e))
            traceback.print_exc()
        finally:
            pythoncom.CoUninitialize()
