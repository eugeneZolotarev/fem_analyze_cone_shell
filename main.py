import win32com.client
import os
import json
import time
import numpy as np

class FemapSession:
    _instance = None
    app = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FemapSession, cls).__new__(cls)
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        try:
            self.app = win32com.client.GetActiveObject("femap.model")
            print("Успешное подключение к активному Femap.")
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            self.app = None

    def is_connected(self):
        return self.app is not None

class Task:
    def __init__(self, file_path):
        self.session = FemapSession()
        self.app = self.session.app
        self.file_path = os.path.abspath(file_path).replace("/", "\\")
        self._create_new_model()
        self.id_generatrix_cone = -1
        self._center_bottom_rbe2_node = -1
        self._center_top_rbe2_node = -1

    def _create_new_model(self):
        print(f"--- Модель: {os.path.basename(self.file_path)} ---")
        try:
            try: self.app.feFileNew()
            except TypeError: pass
            time.sleep(0.5)
            self.app.feAppUpdatePanes(True)
        except Exception as e:
            print(f"Ошибка при создании: {e}")

    def create_material(self, mat_data):
        print(f"Создание материала '{mat_data['name']}'...")
        try:
            mat = self.app.feMatl
            mat.title = mat_data["name"]
            mat.type = 0
            mat.Ex, mat.Nuxy, mat.Density = float(mat_data["E"]), float(mat_data["nu"]), float(mat_data["rho"])
            mat_id = mat.NextEmptyID
            mat.Put(mat_id)
            return mat_id
        except: return None

    def create_property(self, prop_data, material_id):
        name = prop_data["name"]
        print(f"Создание свойства '{name}' ({prop_data['type']})...")
        try:
            prop = self.app.feProp
            prop.title = name
            prop.matlID = material_id
            
            p_type = prop_data["type"].lower()
            if p_type == "plate":
                prop.type = 17
                temp_pmat = list(prop.pmat)
                temp_pmat[0] = float(prop_data["thickness"])
                prop.pmat = temp_pmat
            elif p_type == "beam_z":
                prop.type = 5
                dims = prop_data["dimensions"]
                d_list = [float(dims["h"]), float(dims["w_top"]), float(dims["w_bot"]),
                          float(dims["t_top"]), float(dims["t_bot"]), float(dims["t_web"])]
                temp_vflagI = list(prop.vflagI)
                temp_vflagI[1], temp_vflagI[2] = 13, 1
                prop.vflagI = temp_vflagI
                prop.ComputeStdShape2(True, 13, d_list, 0, 1, True, True, True)
                temp_pmat = list(prop.pmat)
                temp_pmat[40], temp_pmat[41], temp_pmat[42], temp_pmat[43], temp_pmat[44], temp_pmat[45] = d_list
                prop.pmat = temp_pmat

            prop_id = prop.NextEmptyID
            prop.Put(prop_id)
            return prop_id
        except: return None

    def create_conical_surface(self, geom_data):
        """Создает оболочку конуса (Solid + Explode + Delete торцов)."""
        print(f"Создание геометрии...")
        try:
            sizes = [float(geom_data["diameter_big"])/2, float(geom_data["diameter_small"])/2, float(geom_data["height"])]
            self.app.feSolidPrimitive(0, 3, True, [0,0,0], sizes, "Cone")
            
            sol_set = self.app.feSet
            sol_set.Add(1)
            try: self.app.feSolidExplode(sol_set.ID)
            except: pass
            
            self.app.feDelete(39, -3)
            self.app.feDelete(39, -4)
            self.app.feFileRebuild(0, True)
            self.app.feViewRegenerate(0)
            return True
        except: return False

    def mesh_all_surfaces(self, mesh_data, plate_prop_id):
        """Разбивает поверхности на Mapped сетку, управляя каждой границей."""
        print(f"ОТЛАДКА: Управляемый мешинг всех поверхностей...")
        try:
            n_circ = int(mesh_data["divisions_circular"])
            n_height = int(mesh_data["divisions_height"])

            surf_set = self.app.feSet
            surf_set.AddAll(5)  # FT_SURFACE

            surf_obj = self.app.feSurface
            try: surf_set.Reset()
            except: _ = surf_set.Reset

            # Собираем ID поверхностей
            sid_list = []
            while True:
                next_id = surf_set.Next
                if next_id == 0: break
                sid_list.append(next_id)

            for sid in sid_list:
                print(f"Настройка поверхности {sid}:")
                self.app.feMeshAttrSurface(-sid, plate_prop_id, 0.0)
                self.app.feMeshApproachSurface(-sid, 3, [0,0,0,0])

                curve_set = self.app.feSet
                curve_set.AddRule(sid, 8)
                c_count = curve_set.Count

                cid_list = []
                for _ in range(c_count):
                    cid_list.append(curve_set.Next)

                curve = self.app.feCurve
                for cid in cid_list:
                    curve.Get(cid)
                    is_circ = False
                    if curve.IsArc == -1: is_circ = True
                    else:
                        p_ids = curve.vStdPoint
                        p1, p2 = self.app.fePoint, self.app.fePoint
                        p1.Get(p_ids[0]); p2.Get(p_ids[1])
                        if abs(p1.z - p2.z) < 1e-6: is_circ = True
                        else: self.id_generatrix_cone = cid

                    num_div = (n_circ // 2) if is_circ else n_height
                    self.app.feMeshSizeCurve(-cid, num_div, 0.0, 0, 0, 0, 0, 0, 1.0, 0, True)

                self.app.feMeshSurface2(-sid, plate_prop_id, 4, True, False)

            self.app.feViewRegenerate(0)
            return True
        except Exception as e:
            print(f"Ошибка мешинга: {e}")
            return False

    def create_beams_on_generatrix(self, beam_prop_id, beam_height, plate_thickness, beam_width, beam_thickness):
        """Создает балочные элементы with offset."""
        if self.id_generatrix_cone <= 0: return False
            
        print(f"Создание балок со смещением на образующей {self.id_generatrix_cone}...")
        
        curve = self.app.feCurve
        curve.Get(self.id_generatrix_cone)
        p_ids = curve.vStdPoint
        p1, p2 = self.app.fePoint, self.app.fePoint
        p1.Get(p_ids[0]); p2.Get(p_ids[1])

        # 1. Создаем балки
        orient_vec = [0.0, 1.0, 0.0]
        rc = self.app.feMeshCurve2(-self.id_generatrix_cone, 5, beam_prop_id, True, 0, orient_vec)

        if rc == -1:
            # 2. Собираем элементы на кривой
            elem_set = self.app.feSet
            elem_set.AddRule(self.id_generatrix_cone, 43)
            
            try: e_count = elem_set.Count()
            except: e_count = elem_set.Count
            print(f"Найдено балок для настройки: {e_count}")

            tangens_vector = np.array([p1.x - p2.x, p1.y - p2.y, p1.z - p2.z])
            vecY = np.array([0.0, 1.0, 0.0])
            vecDir = np.cross(tangens_vector, vecY)
            norm = np.linalg.norm(vecDir)
            vecDir /= norm

            offset_dist1 = - (beam_height + plate_thickness) / 2
            offset_dist2 = - (beam_width - beam_thickness) / 2

            off_vec1 = [
                float(vecDir[0] * offset_dist1 + vecY[0] * offset_dist2),
                float(vecDir[1] * offset_dist1 + vecY[1] * offset_dist2),
                float(vecDir[2] * offset_dist1 + vecY[2] * offset_dist2)
            ]

            # 3. Применяем смещение
            self.app.feModifyOffsets(elem_set.ID, True, True, False, off_vec1, off_vec1)
            print(f"Смещение {off_vec1} применен к балкам.")

        self.app.feViewRegenerate(0)
        print("Метод create_beams_on_generatrix завершен.")
        return True

    def create_beam_array(self, stringers_count):
        """Создает круговой массив балок."""
        if self.id_generatrix_cone <= 0 or stringers_count <= 1: 
            return False
            
        print(f"Создание кругового массива балок ({stringers_count} шт.)...")
        try:
            try: count_before = self.app.feElem.CountSet()
            except: count_before = self.app.feElem.CountSet
            
            elem_set = self.app.feSet
            elem_set.AddRule(self.id_generatrix_cone, 43)
            
            copy_tool = self.app.feCopyTool
            copy_tool.Repetitions = int(stringers_count) - 1
            
            base = [0.0, 0.0, 0.0]
            direction = [0.0, 0.0, 1.0]
            angle = 360.0 / float(stringers_count)
            
            rc = copy_tool.RotateAroundVector(8, elem_set.ID, base, direction, angle, 0.0)
            
            try: count_after = self.app.feElem.CountSet()
            except: count_after = self.app.feElem.CountSet
            
            print(f"Элементов до: {count_before}, после: {count_after}")
            
            if count_after > count_before:
                print(f"Круговой массив успешно создан. Добавлено {count_after - count_before} элементов.")
                return True
            else:
                print(f"ОШИБКА: Количество элементов не изменилось. Код возврата: {rc}")
                return False
        except Exception as e:
            print(f"Исключение в create_beam_array: {e}")
            return False

    def create_rigid_elements(self):
        """Создает 2 RBE2 элемента: один для нижнего торца и один для верхнего."""
        print("Создание жестких элементов (RBE2)...")

        import Pyfemap
        try:
            # Передаем сырой COM-указатель внутрь класса Pyfemap
            nd = Pyfemap.INode(self.app.feNode._oleobj_)
            rc, numNode, entID, xyz = nd.GetCoordArray(0)

            if rc == -1:
                # Генератор словаря: {ID_узла: (X, Y, Z)}
                nodes_dict = {
                    entID[i]: (xyz[3 * i], xyz[3 * i + 1], xyz[3 * i + 2])
                    for i in range(numNode)
                }

                z_min = min(coords[2] for coords in nodes_dict.values())
                z_max = max(coords[2] for coords in nodes_dict.values())
                nodes_bottom_cone = dict(filter(lambda element: abs(element[1][2] - z_min) < 1e-7, nodes_dict.items()))
                nodes_top_cone = dict(filter(lambda element: abs(element[1][2] - z_max) < 1e-7, nodes_dict.items()))

                # 3. Создаем независимые узлы в центрах
                node_obj = self.app.feNode
                self._center_bottom_rbe2_node = node_obj.NextEmptyID
                node_obj.x, node_obj.y, node_obj.z = 0.0, 0.0, z_min
                node_obj.Put(self._center_bottom_rbe2_node)

                self._center_top_rbe2_node = node_obj.NextEmptyID
                node_obj.x, node_obj.y, node_obj.z = 0.0, 0.0, z_max
                node_obj.Put(self._center_top_rbe2_node)

                # 4. Создаем два RBE2 элемента
                for center_id, dep_nodes, label in [
                    (self._center_bottom_rbe2_node, list(nodes_bottom_cone.keys()), "Нижний"),
                    (self._center_top_rbe2_node, list(nodes_top_cone.keys()), "Верхний")
                ]:
                    if not dep_nodes: continue

                    elem = self.app.feElem
                    el_id = elem.NextEmptyID
                    elem.type = 29      # Rigid
                    elem.topology = 13  # RigidList

                    # Устанавливаем независимый узел
                    nodes = list(elem.vnode)
                    nodes[0] = center_id
                    elem.vnode = nodes

                    n_count = len(dep_nodes)
                    # 63 = все 6 DOF для каждого зависимого узла
                    elem.PutNodeList(0, n_count, dep_nodes, [0]*n_count, [1.0]*n_count, [63]*n_count)
                    elem.Put(el_id)
                    print(f"RBE2 {label} (ID {el_id}) создан: {n_count} зависимых узлов.")

                return True
            return False

        except Exception as e:
            return False

    def apply_axial_load(self, force_value):
        """Прикладывает осевую нагрузку к верхнему центральному узлу RBE2."""
        if self._center_top_rbe2_node <= 0:
            print("ОШИБКА: Верхний центральный узел не найден.")
            return False
            
        print(f"Приложение осевой нагрузки {force_value} к узлу {self._center_top_rbe2_node}...")

        # 1. Создаем или получаем активный набор нагрузок (Load Set)
        ls = self.app.feLoadSet
        ls_id = ls.NextEmptyID
        ls.title = "Мой набор нагрузок"
        ls.Put(ls_id)
        # Делаем этот набор активным
        ls.Active = ls_id

        # 2. Инициализируем объект узловой/элементной нагрузки
        lm = self.app.feLoadMesh
        # Привязываем создаваемую нагрузку к ID нашего набора
        lm.setID = ls_id

        # 3. Подготавливаем аргументы
        # Константа FLT_NFORCE (сосредоточенная узловая сила) имеет числовое значение 1 [3]
        load_type = 1
        csys_id = 0  # Базовая глобальная система координат

        # Массивы должны иметь строго заданную длину, требуемую COM-интерфейсом [4]
        dof_array = [True, True, True]  # 3 флага (вкл/выкл) для осей X, Y, Z [4]
        values_array = [0.0, 0.0, force_value, 0.0, 0.0]  # 5 значений: компоненты X, Y, Z и два обязательных нуля [4]
        func_array = [0, 0, 0, 0, 0]

        # 4. Применяем нагрузку к узлу (ОБРАТИТЕ ВНИМАНИЕ НА МИНУС)
        rc = lm.Add(-self._center_top_rbe2_node, load_type, csys_id, dof_array, values_array, func_array)

        if rc == -1:  # Константа FE_OK
            print(f"Нагрузка успешно приложена к узлу {self._center_top_rbe2_node}")

    def apply_constraints(self):
        """Закрепляет нижний центральный узел RBE2 по всем 6 степеням свободы."""
        if self._center_bottom_rbe2_node <= 0:
            print("ОШИБКА: Нижний центральный узел не найден.")
            return False
            
        print(f"Приложение закреплений к нижнему узлу {self._center_bottom_rbe2_node} (6 DOF)...")
        
        # 1. Создаем набор закреплений (BC Set)
        bcs = self.app.feBCSet
        bcs_id = bcs.NextEmptyID
        bcs.title = "Fixed Base"
        bcs.Put(bcs_id)
        # Делаем этот набор активным
        bcs.Active = bcs_id

        # 2. Создаем узловое закрепление (feBCNode)
        bn = self.app.feBCNode
        bn.setID = bcs_id
        
        # Add(-nodeID, DOF1, DOF2, DOF3, DOF4, DOF5, DOF6)
        rc = bn.Add(-self._center_bottom_rbe2_node, True, True, True, True, True, True)
        
        if rc == -1:
            print("Закрепления успешно приложены.")
            return True
        else:
            print(f"Ошибка при приложении закреплений. Код: {rc}")
            return False

    def merge_nodes(self, tolerance=1e-6):
        """Сшивает совпадающие узлы во всей модели."""
        print(f"Сшивка совпадающих узлов (допуск {tolerance})...")
        
        # 1. Собираем все узлы модели (7 = FT_NODE)
        node_set = self.app.feSet
        node_set.AddAll(7)
        
        # 2. Вызываем метод сшивки
        # feCheckCoincidentNode2(setID, tolerance, bMerge, mergeMode, mergeLoc, bAcrossConn, messageMode, bSaveGroups)
        # mergeMode: 1 = Keep Lower ID
        # mergeLoc: 1 = Keep Lower ID Location
        rc = self.app.feCheckCoincidentNode2(node_set.ID, tolerance, True, 1, 1, True, 1, False)
        
        if rc == -1:
            print("Сшивка узлов успешно завершена.")
            return True
        else:
            print(f"Предупреждение: Метод сшивки вернул код {rc}")
            return False

    def configure_view(self):
        """Настраивает визуализацию."""
        print("Настройка визуализации вида...")
        surf_set = self.app.feSet
        surf_set.AddAll(5)
        self.app.feEntitySetVisibility(5, surf_set.ID, False, True)
        view_obj = self.app.feView
        view_obj.Reset
        while True:
            has_v = view_obj.Next
            if not has_v: break
            vid = view_obj.ID
            labels = list(view_obj.vLabel); labels[12] = 3; view_obj.vLabel = labels
            view_obj.Put(vid)
            print(f"Вид ID {vid} настроен.")
        self.app.feViewRegenerate(0)
        return True

    def save_active(self):
        try:
            self.app.feFileSaveAs(0, self.file_path)
            self.app.feAppUpdatePanes(True)
        except: pass

def run_automation(config_path):
    if not os.path.exists(config_path): return
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    global_mat = config.get("material")
    properties_list = config.get("properties", [])
    geom_data = config.get("geometry")
    mesh_data = config.get("mesh")
    load_data = config.get("loads")
    
    if config.get("tasks"):
        task_data = config["tasks"][0]
        models_dir = os.path.join(os.getcwd(), "models")
        if not os.path.exists(models_dir): os.makedirs(models_dir)
        
        file_path = os.path.join(models_dir, task_data["file_name"])
        task = Task(file_path)
        
        if task.session.is_connected():
            mat_id = task.create_material(global_mat)
            plate_prop_id, beam_prop_id = None, None
            beam_h, plate_t, beam_w, beam_t_web = 0.0, 0.0, 0.0, 0.0
            for p_data in properties_list:
                p_id = task.create_property(p_data, mat_id)
                if p_data["type"].lower() == "plate":
                    plate_prop_id, plate_t = p_id, p_data["thickness"]
                if p_data["type"].lower() == "beam_z":
                    beam_prop_id, beam_h = p_id, p_data["dimensions"]["h"]
                    beam_w, beam_t_web = p_data["dimensions"]["w_bot"], p_data["dimensions"]["t_web"]

            if task.create_conical_surface(geom_data):
                task.mesh_all_surfaces(mesh_data, plate_prop_id)
                if beam_prop_id:
                    if task.create_beams_on_generatrix(beam_prop_id, beam_h, plate_t, beam_w, beam_t_web):
                        s_count = mesh_data.get("stringers_count", 0)
                        if s_count > 1:
                            task.create_beam_array(s_count)
                
                # Сшиваем узлы перед созданием RBE2
                task.merge_nodes()
                
                if task.create_rigid_elements():
                    if load_data and "axial_force" in load_data:
                        task.apply_axial_load(load_data["axial_force"])
                    # Применяем закрепления в нижней точке
                    task.apply_constraints()
            
            task.configure_view()
            task.save_active()

if __name__ == "__main__":
    run_automation("config.json")
