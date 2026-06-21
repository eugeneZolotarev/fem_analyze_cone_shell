import numpy as np
import os
import csv
from builders import ConeModelBuilder
from mesh_test_director import MeshTestDirector

if __name__ == '__main__':
    builder = ConeModelBuilder()
    director = MeshTestDirector(builder)

    geometry = {"height": 1036.0, "diameter_small": 1281.0,
                "diameter_big": 1507.0}
    material = {"name": "Aluminium", "E": 78000.0, "nu": 0.3,
                "rho": 2470, "yield": 270.0}
    loads = {"axial_force": -700000.0}

    t_min, t_max, t_step = 1, 5, 0.1
    skin_range = np.arange(t_min, t_max + t_step, t_step).tolist()

    n_min, n_max, n_step = 10, 10, 20
    str_counts = list(range(n_min, n_max + 1, n_step))

    s_count = 10 #пока интересует 10 стрингеров
    
    # ПРАВИЛЬНЫЙ ПУТЬ: определяем папку скрипта и кладем CSV в нее
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(current_dir, "mesh_test.csv")
    
    print(f"Файл результатов будет сохранен здесь: {csv_file}")
    
    # Записываем заголовок, если файл пустой или не существует
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists or os.path.getsize(csv_file) == 0:
            writer.writerow(["Elements_Between", "Elements_Along", "Eigenvalue"])

    for eb in range (16, 17):
        for ea in range (44, 45):
            print(f"Тест сетки: EB={eb}, EA={ea}...")

            profile_formatted = {
                "name": "Profile_450016",
                "type": "beam_z",
                "dimensions": {
                    "h": float(25.0),
                    "w_bot": float(20.0),
                    "w_top": float(20.0),
                    "t_bot": float(3.0),
                    "t_web": float(2.0),
                    "t_top": float(3.0)
                }
            }

            params = {"geometry": geometry, "material": material, "loads": loads, "skin_range": skin_range,
                      "str_counts": str_counts,
                      "profiles": [], "elements_between": eb, "elements_along": ea,
                      "ui_t_min": t_min, "ui_t_max": t_max, "ui_t_step": t_step,
                      "ui_n_min": n_min, "ui_n_max": n_max, "ui_n_step": n_step,
                      "resume_t_idx": 0, "resume_n_idx": 0, "resume_p_idx": 0,
                      "nastran_path": ""}

            t_min_limit = float(params.get("ui_t_min", 1.0))

            iter_params = {
                "geometry": params["geometry"].copy(),
                "material": params["material"].copy(),
                "loads": params["loads"].copy(),
                "mesh": {
                    "divisions_circular": int(s_count * eb),
                    "divisions_height": int(ea)
                },
                "plate_prop": {
                    "name": "Shell", "type": "plate", "thickness": t_min_limit
                },
                "beam_prop": profile_formatted,
                "optimization": {
                    "t_min": t_min_limit,
                    "t_max": params["ui_t_max"]
                }
            }
            iter_params["geometry"]["stringer_count"] = s_count

            res = director.construct_and_solve(iter_params)
            
            if res:
                eig = res.get("eigenvalue", 0.0)
                print(f"Результат: Eig={eig:.6f}")
                # Дозаписываем результат в файл
                with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([eb, ea, eig])
            else:
                print(f"Ошибка на итерации EB={eb}, EA={ea}")
