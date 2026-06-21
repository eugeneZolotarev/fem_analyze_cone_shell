import os
import time
import json
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

    def _save_checkpoint(self, p_idx, n_idx):
        """Сохраняет текущий прогресс в файл."""
        try:
            checkpoint_data = self.params.copy()
            checkpoint_data["resume_p_idx"] = p_idx
            checkpoint_data["resume_n_idx"] = n_idx
            with open("checkpoint.json", "w", encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения чекпоинта: {e}")

    def run(self):
        pythoncom.CoInitialize()
        try:
            builder = ConeModelBuilder(params=self.params)
            director = OptimizationDirector(builder)
            
            stringer_counts = self.params.get("str_counts", [])
            raw_profiles = self.params.get("profiles", [])
            total_tasks = len(stringer_counts) * len(raw_profiles)
            
            # Считываем индексы возобновления
            resume_p = self.params.get("resume_p_idx", 0)
            resume_n = self.params.get("resume_n_idx", 0)
            
            self.log_message.emit(f"Запуск оптимизации: {total_tasks} вариантов (Старт с P:{resume_p}, N:{resume_n}).")
            
            current_idx = 0
            t_min_limit = float(self.params.get("ui_t_min", 1.0))
            f_safety = 1.0 

            for p_idx, raw_profile in enumerate(raw_profiles):
                if p_idx < resume_p:
                    current_idx += len(stringer_counts)
                    continue
                
                p_name = raw_profile.get("Номер профиля", "Unknown")
                
                for s_idx, s_count in enumerate(stringer_counts):
                    # Пропускаем уже посчитанные N для текущего возобновляемого профиля
                    if p_idx == resume_p and s_idx < resume_n:
                        current_idx += 1
                        continue
                        
                    if not self._is_running: 
                        self._save_checkpoint(p_idx, s_idx)
                        return
                    
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
                            "divisions_circular": int(s_count * self.params["elements_between"]),
                            "divisions_height": int(self.params["elements_along"])
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
                        E, nu, rho, sigma_y = float(mat["E"]), float(mat["nu"]), float(mat["rho"]), float(mat["yield"])
                        
                        plate_max = res["max_stress"]
                        plate_ms = (sigma_y / (plate_max * f_safety)) - 1 if plate_max > 0 else 0
                        
                        beam_max = abs(res["beam_max_stress"])
                        beam_ms = (sigma_y / (beam_max * f_safety)) - 1 if beam_max > 0 else 0
                        
                        d = profile_formatted["dimensions"]
                        sigma_cr_flange = 0.46 * ((np.pi**2 * E) / (12 * (1 - nu**2))) * (d["t_top"] / d["w_top"])**2
                        flange_buckling_ms = (sigma_cr_flange / (beam_max * f_safety)) - 1 if beam_max > 0 else 0

                        # Масса
                        # geom = self.params["geometry"]
                        # H, R, r = float(geom["height"]), float(geom["diameter_big"])/2, float(geom["diameter_small"])/2
                        # L_cone = np.sqrt((R-r)**2 + H**2)
                        # Area_shell = np.pi * (R + r) * L_cone
                        # mmass_stringer_per_1mm = float(raw_profile["Теоретическая масса 1 м, кг"]["Алюминиевый сплав"]) * 1.0e-6
                        # mass_kg = (Area_shell * t_opt * rho + s_count * mmass_stringer_per_1mm * L_cone) * 1000 #получаем значение в тоннах поэтому и делим на 1000
                        # print(mass_kg)
                        # print(Area_shell * t_opt * rho + s_count)
                        # print(s_count * mmass_stringer_per_1mm * L_cone)

                        mass_kg = res["total_mass"] * 1000 # переводим тонну в кг

                        end_time = time.time()
                        
                        self.result_ready.emit({
                            "current_idx": current_idx, "total_tasks": total_tasks,
                            "t": t_opt, "n": s_count, "profile": p_name,
                            "max_stress": plate_max, "beam_max_stress": beam_max, "eigenvalue": res["eigenvalue"],
                            "plate_sf": plate_ms, "beam_sf": beam_ms, "flange_buckling_sf": flange_buckling_ms,
                            "total_mass": mass_kg, "difference_time": f"{int(end_time - start_time)}s",
                            "skin_thickness": t_opt, "stringer_count": s_count, "profile_name": p_name
                        })
                        
                        # Обновляем чекпоинт на следующую под-задачу
                        self._save_checkpoint(p_idx, s_idx + 1)

                        if abs(t_opt - t_min_limit) < 1e-7:
                            self.log_message.emit(f"Профиль {p_name}: t_min достигнут. Переход к след. профилю.")
                            remaining_s = len(stringer_counts) - (s_idx + 1)
                            current_idx += remaining_s
                            self._save_checkpoint(p_idx + 1, 0) # Переходим к следующему профилю
                            break
                    
                    self.progress_updated.emit(int((current_idx / total_tasks) * 100))
            
            # Если всё дочитали, удаляем чекпоинт
            if os.path.exists("checkpoint.json"):
                os.remove("checkpoint.json")
            self.finished.emit()
            
        except Exception as e:
            self.log_message.emit(f"Ошибка: {e}")
            self.error_occurred.emit(str(e))
            traceback.print_exc()
        finally:
            pythoncom.CoUninitialize()
