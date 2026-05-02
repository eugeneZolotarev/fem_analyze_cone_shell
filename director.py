import os
import time

class OptimizationDirector:
    def __init__(self, builder):
        self.builder = builder

    def construct_and_solve(self, params):
        dat_path = ""
        try:
            # 1. Сборка модели
            if not self.builder.init_new_model(): return None
            mid = self.builder.create_material(params["material"])
            ppid = self.builder.create_property(params["plate_prop"], mid)
            bpid = self.builder.create_property(params["beam_prop"], mid)
            
            if not self.builder.build_geometry(params["geometry"]): return None
            if not self.builder.build_mesh(params["mesh"], ppid): return None
            
            # Stringers
            d = params["beam_prop"]["dimensions"]
            self.builder.build_stringers(bpid, d["h"], d["w_bot"], d["t_bot"], d["t_web"], d["t_top"], params["geometry"]["stringer_count"])
            
            self.builder.merge_nodes()
            self.builder.create_rigid_connections()
            
            lsid = self.builder.apply_loads(params["loads"])
            csid = self.builder.apply_constraints()
            
            # 2. Настройка анализа и оптимизация Nastran SOL 200
            models_dir = os.path.join(os.getcwd(), "models")
            if not os.path.exists(models_dir): os.makedirs(models_dir)
            
            model_name = f"opt_{int(time.time())}"
            dat_path = os.path.join(models_dir, f"{model_name}.dat")
            
            am_id = self.builder.setup_analysis(lsid, csid, dat_path)
            
            opt_params = {
                't_min': params['optimization']['t_min'],
                't_max': params['optimization']['t_max'],
                'sigma_y': params['material'].get('yield', 0.0) 
            }
            
            # Экспорт и запуск SOL 200
            if not self.builder.export_and_modify_nastran(am_id, dat_path, opt_params): return None
            if not self.builder.run_external_nastran(dat_path): return None
            
            # 3. ПОЛУЧЕНИЕ НОВОЙ ТОЛЩИНЫ И ОБНОВЛЕНИЕ МОДЕЛИ
            opt_thickness = self.builder.get_optimized_thickness(dat_path)
            if opt_thickness > 0:
                self.builder.update_property_thickness(ppid, opt_thickness)
            
            # 4. ЗАПУСК ПОВЕРОЧНОГО РАСЧЕТА (Verification SOL 105)
            # Принудительно устанавливаем метод анализа на устойчивость (6)
            mgr = self.builder.app.feAnalysisMgr
            if mgr.Get(am_id) == -1:
                mgr.NasModeMethod = 6
                mgr.Put(am_id)
            
            if not self.builder.run_analysis(am_id):
                print("WARNING: Поверочный расчет не завершился корректно.")
            
            # 5. Считывание финальных результатов
            results = self.builder.read_results()
            results["optimized_thickness"] = opt_thickness
            
            self.builder.configure_view()
            
            # 6. ОЧИСТКА (Выполняется перед return)
            self.builder.close_model()
            if dat_path:
                self.builder.delete_model_file(dat_path)
            
            return results

        except Exception as e:
            print(f"Director error: {e}")
            # Пытаемся закрыть модель даже при ошибке
            try: self.builder.close_model()
            except: pass
            return None
