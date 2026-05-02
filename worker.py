import time
import pythoncom
import traceback
import numpy as np
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
            t_min_limit = float(self.params.get("ui_t_min", 1.0))

            for p_idx, raw_profile in enumerate(raw_profiles):
                p_name = raw_profile.get("Номер профиля", "Unknown")
                for s_idx, s_count in enumerate(stringer_counts):
                    if not self._is_running: break
                    
                    current_idx += 1
                    start_time = time.time()
                    
                    profile_formatted = {
                        "name": f"Profile_{p_name}",
                        "type": "beam_z",
                        "dimensions": {
                            "h": float(raw_profile["H, мм"]),
                            "w_bot": float(raw_profile["B, мм"]),
                            "w_top": float(raw_profile["B, мм"]),
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
                            "name": "Shell", "type": "plate", "thickness": t_min_limit
                        },
                        "beam_prop": profile_formatted,
                        "optimization": {
                            "t_min": t_min_limit,
                            "t_max": self.params["ui_t_max"]
                        }
                    }
                    iter_params["geometry"]["stringer_count"] = s_count

                    self.log_message.emit(f"Расчет {current_idx}/{total_tasks}: Prof={p_name}, N={s_count}")
                    
                    res = director.construct_and_solve(iter_params)
                    
                    if res:
                        t_opt = res.get("optimized_thickness", 0.0)
                        mat = self.params["material"]
                        E = float(mat["E"])
                        nu = float(mat["nu"])
                        rho = float(mat["rho"])
                        sigma_y = float(mat["yield"])
                        
                        # 1. MS по текучести для оболочки (Plate)
                        plate_max = res["max_stress"]
                        plate_ms = (sigma_y / plate_max) - 1 if plate_max > 0 else 0
                        
                        # 2. MS по текучести для стрингеров (Beam)
                        beam_max = abs(res["beam_max_stress"])
                        beam_ms = (sigma_y / beam_max) - 1 if beam_max > 0 else 0
                        
                        # 3. MS местной устойчивости полки стрингера (Local Buckling)
                        d = profile_formatted["dimensions"]
                        sigma_cr_flange = 0.46 * ((np.pi**2 * E) / (12 * (1 - nu**2))) * (d["t_top"] / d["w_top"])**2
                        flange_buckling_ms = (sigma_cr_flange / beam_max) - 1 if beam_max > 0 else 0

                        # Расчет массы
                        g = self.params["geometry"]
                        H = float(g["height"])
                        R = float(g["diameter_big"]) / 2
                        r = float(g["diameter_small"]) / 2
                        L_cone = np.sqrt((R-r)**2 + H**2)
                        Area_shell = np.pi * (R + r) * L_cone
                        
                        # Площадь сечения стрингера из raw_profile в см2 -> мм2
                        Area_stringer_mm2 = float(raw_profile["Площадь сечения, см2"]) * 100
                        
                        mass_kg = (Area_shell * t_opt * rho + s_count * Area_stringer_mm2 * L_cone * rho) * 1e-9

                        end_time = time.time()
                        
                        result_data = {
                            "current_idx": current_idx,
                            "total_tasks": total_tasks,
                            "t": t_opt,
                            "n": s_count,
                            "profile": p_name,
                            "max_stress": plate_max,
                            "beam_max_stress": beam_max,
                            "eigenvalue": res["eigenvalue"],
                            "plate_sf": plate_ms,
                            "beam_sf": beam_ms,
                            "flange_buckling_sf": flange_buckling_ms,
                            "total_mass": mass_kg,
                            "difference_time": f"{int(end_time - start_time)}s",
                            "skin_thickness": t_opt,
                            "stringer_count": s_count,
                            "profile_name": p_name
                        }
                        self.result_ready.emit(result_data)
                        
                        if abs(t_opt - t_min_limit) < 1e-7:
                            self.log_message.emit(f"Профиль {p_name}: t_min достигнут. Пропуск.")
                            remaining_s = len(stringer_counts) - (s_idx + 1)
                            current_idx += remaining_s
                            break
                    
                    self.progress_updated.emit(int((current_idx / total_tasks) * 100))
                    
            self.finished.emit()
            
        except Exception as e:
            self.log_message.emit(f"Ошибка: {e}")
            self.error_occurred.emit(str(e))
            traceback.print_exc()
        finally:
            pythoncom.CoUninitialize()
