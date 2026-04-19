import os

class ModelDirector:
    """Оркестратор, возвращающий результаты расчета."""
    
    def __init__(self, builder):
        self.builder = builder

    def construct_and_solve(self, config, output_path):
        """Основной цикл: возвращает макс. напряжение или None."""
        
        # 1. Инициализация
        if not self.builder.init_new_model(): return None

        # 2. Материалы и Свойства
        mat_id = self.builder.create_material(config.get("material"))
        
        props = config.get("properties", [])
        plate_prop_id, beam_prop_id = None, None
        beam_h, plate_t, beam_w, beam_t_web = 0.0, 0.0, 0.0, 0.0
        
        for p in props:
            p_id = self.builder.create_property(p, mat_id)
            if p["type"].lower() == "plate":
                plate_prop_id, plate_t = p_id, p["thickness"]
            elif p["type"].lower() == "beam_z":
                beam_prop_id = p_id
                beam_h = p["dimensions"]["h"]
                beam_w = p["dimensions"]["w_bot"]
                beam_t_web = p["dimensions"]["t_web"]

        # 3. Геометрия и сетка
        if not self.builder.build_geometry(config.get("geometry")): return None
        self.builder.build_mesh(config.get("mesh"), plate_prop_id)
        
        if beam_prop_id:
            s_count = config.get("mesh", {}).get("stringers_count", 0)
            self.builder.build_stringers(beam_prop_id, beam_h, plate_t, beam_w, beam_t_web, s_count)
            
        # 4. Сшивка и Жесткие связи
        self.builder.merge_nodes()
        if not self.builder.create_rigid_connections(): return None
            
        # 5. Нагрузки и Закрепления
        ls_id = self.builder.apply_loads(config.get("loads"))
        cs_id = self.builder.apply_constraints()
        
        # 6. Сохранение и Расчет
        self.builder.save_model(output_path)
        
        max_stress = 0.0
        if ls_id and cs_id:
            am_id = self.builder.setup_analysis(ls_id, cs_id, output_path)
            if self.builder.run_analysis(am_id, output_path):
                # СЧИТЫВАЕМ РЕЗУЛЬТАТЫ ПОКА МОДЕЛЬ ОТКРЫТА
                max_stress = self.builder.read_results()
        
        # 7. Финализация и ОЧИСТКА
        self.builder.configure_view()
        self.builder.save_model(output_path) 
        self.builder.close_model()
        self.builder.delete_model_file(output_path)
        
        return max_stress
