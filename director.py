import os

class ModelDirector:
    """Оркестратор, управляющий процессом сборки и расчета модели."""
    
    def __init__(self, builder):
        self.builder = builder

    def construct_and_solve(self, config, output_path):
        """Основной цикл: от инициализации до результатов."""
        
        # 1. Инициализация (создание нового файла .modfem)
        if not self.builder.init_new_model():
            return False

        # 2. Материалы и Свойства
        mat_data = config.get("material")
        mat_id = self.builder.create_material(mat_data)
        
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

        # 3. Геометрия
        if not self.builder.build_geometry(config.get("geometry")):
            return False
            
        # 4. Сетка и Стрингеры
        mesh_data = config.get("mesh")
        self.builder.build_mesh(mesh_data, plate_prop_id)
        
        if beam_prop_id:
            s_count = mesh_data.get("stringers_count", 0)
            self.builder.build_stringers(beam_prop_id, beam_h, plate_t, beam_w, beam_t_web, s_count)
            
        # 5. Сшивка и Жесткие связи
        self.builder.merge_nodes()
        if not self.builder.create_rigid_connections():
            return False
            
        # 6. Нагрузки и Закрепления
        ls_id = self.builder.apply_loads(config.get("loads"))
        cs_id = self.builder.apply_constraints()
        
        # 7. Расчет
        if ls_id and cs_id:
            am_id = self.builder.setup_analysis(ls_id, cs_id)
            if self.builder.run_analysis(am_id):
                # 8. Результаты
                self.builder.read_results()
        
        # 9. Финализация
        self.builder.configure_view()
        self.builder.save_model(output_path)
        print(f"--- Модель успешно завершена: {os.path.basename(output_path)} ---")
        return True
