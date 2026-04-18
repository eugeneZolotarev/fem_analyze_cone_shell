import os
import time
import traceback
import numpy as np
from abc import ABC, abstractmethod
from session import FemapSession

class ModelBuilder(ABC):
    """Абстрактный интерфейс строителя расчетной модели."""
    
    @abstractmethod
    def init_new_model(self): pass
    
    @abstractmethod
    def create_material(self, mat_data): pass
    
    @abstractmethod
    def create_property(self, prop_data, material_id): pass
    
    @abstractmethod
    def build_geometry(self, geom_data): pass
    
    @abstractmethod
    def build_mesh(self, mesh_data, plate_prop_id): pass
    
    @abstractmethod
    def build_stringers(self, beam_prop_id, beam_h, plate_t, beam_w, beam_t_web, s_count): pass
    
    @abstractmethod
    def merge_nodes(self, tolerance=1e-6): pass
    
    @abstractmethod
    def create_rigid_connections(self): pass
    
    @abstractmethod
    def apply_loads(self, load_data): pass
    
    @abstractmethod
    def apply_constraints(self): pass
    
    @abstractmethod
    def setup_analysis(self, load_set_id, constraint_set_id): pass
    
    @abstractmethod
    def run_analysis(self, am_id): pass
    
    @abstractmethod
    def read_results(self): pass
    
    @abstractmethod
    def configure_view(self): pass
    
    @abstractmethod
    def save_model(self, file_path): pass

class ConeModelBuilder(ModelBuilder):
    """Строитель модели усеченного конуса со стрингерами."""
    
    def __init__(self):
        self.session = FemapSession()
        self.app = self.session.app
        self.id_generatrix_cone = -1
        self._center_bottom_rbe2_node = -1
        self._center_top_rbe2_node = -1
        self.load_set_id = None
        self.constraint_set_id = None

    def init_new_model(self):
        """Создает новый файл модели (аналог _create_new_model из эталона)."""
        print("Инициализация новой модели Femap...")
        try:
            try: self.app.feFileNew()
            except TypeError: pass
            time.sleep(0.5)
            self.app.feAppUpdatePanes(True)
            return True
        except Exception as e:
            print(f"Ошибка при создании новой модели: {e}")
            return False

    def create_material(self, mat_data):
        print(f"Создание материала '{mat_data['name']}'...")
        try:
            mat = self.app.feMatl
            mat.title = mat_data["name"]
            mat.type = 0
            mat.Ex, mat.Nuxy, mat.Density = float(mat_data["E"]), float(mat_data["nu"]), float(mat_data["rho"])
            mat_id = mat.NextEmptyID()
            mat.Put(mat_id)
            return mat_id
        except Exception as e:
            print(f"Ошибка при создании материала: {e}")
            print(traceback.format_exc())
            return None

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
                prop.pmat = tuple(temp_pmat)
            elif p_type == "beam_z":
                prop.type = 5
                dims = prop_data["dimensions"]
                d_list = (float(dims["h"]), float(dims["w_top"]), float(dims["w_bot"]),
                          float(dims["t_top"]), float(dims["t_bot"]), float(dims["t_web"]))
                temp_vflagI = list(prop.vflagI)
                temp_vflagI[1], temp_vflagI[2] = 13, 1
                prop.vflagI = temp_vflagI
                prop.ComputeStdShape2(True, 13, d_list, 0, 1, True, True, True)
                temp_pmat = list(prop.pmat)
                temp_pmat[40], temp_pmat[41], temp_pmat[42], temp_pmat[43], temp_pmat[44], temp_pmat[45] = d_list
                prop.pmat = temp_pmat

            prop_id = prop.NextEmptyID()
            prop.Put(prop_id)
            return prop_id
        except: return None

    def build_geometry(self, geom_data):
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

    def build_mesh(self, mesh_data, plate_prop_id):
        print(f"ОТЛАДКА: Управляемый мешинг всех поверхностей...")
        n_circ = int(mesh_data["divisions_circular"])
        n_height = int(mesh_data["divisions_height"])

        surf_set = self.app.feSet
        surf_set.AddAll(5)

        sid_list = []
        surf_set.Reset()
        while True:
            next_id = surf_set.Next()
            if next_id == 0: break
            sid_list.append(next_id)

        for sid in sid_list:
            print(f"Настройка поверхности {sid}:")
            self.app.feMeshAttrSurface(-sid, plate_prop_id, 0.0)
            self.app.feMeshApproachSurface(-sid, 3, (0,0,0,0))

            curve_set = self.app.feSet
            curve_set.AddRule(sid, 8)
            curve_set.Reset()
            c_count = curve_set.Count()

            cid_list = []
            for _ in range(c_count):
                cid_list.append(curve_set.Next())

            curve = self.app.feCurve
            for cid in cid_list:
                curve.Get(cid)
                is_circ = False
                if curve.IsArc() == -1: is_circ = True
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

    def build_stringers(self, beam_prop_id, beam_h, plate_t, beam_w, beam_t_web, s_count):
        if self.id_generatrix_cone <= 0: return False
        print(f"Создание балок со смещением на образующей {self.id_generatrix_cone}...")
        
        curve = self.app.feCurve
        curve.Get(self.id_generatrix_cone)
        p_ids = curve.vStdPoint
        p1, p2 = self.app.fePoint, self.app.fePoint
        p1.Get(p_ids[0]); p2.Get(p_ids[1])

        orient_vec = [0.0, 1.0, 0.0]
        rc = self.app.feMeshCurve2(-self.id_generatrix_cone, 5, beam_prop_id, True, 0, orient_vec)

        if rc == -1:
            elem_set = self.app.feSet
            elem_set.AddRule(self.id_generatrix_cone, 43)
            
            tangens_vector = np.array([p1.x - p2.x, p1.y - p2.y, p1.z - p2.z])
            vecY = np.array([0.0, 1.0, 0.0])
            vecDir = np.cross(tangens_vector, vecY)
            vecDir /= np.linalg.norm(vecDir)

            off_dist1 = - (beam_h + plate_t) / 2
            off_dist2 = - (beam_w - beam_t_web) / 2
            off_vec = [float(vecDir[0]*off_dist1 + vecY[0]*off_dist2),
                       float(vecDir[1]*off_dist1 + vecY[1]*off_dist2),
                       float(vecDir[2]*off_dist1 + vecY[2]*off_dist2)]

            self.app.feModifyOffsets(elem_set.ID, True, True, False, off_vec, off_vec)
            
            if s_count > 1:
                copy_tool = self.app.feCopyTool
                copy_tool.Repetitions = int(s_count) - 1
                copy_tool.RotateAroundVector(8, elem_set.ID, [0,0,0], [0,0,1], 360.0/s_count, 0.0)

        self.app.feViewRegenerate(0)
        return True

    def merge_nodes(self, tolerance=1e-6):
        print(f"Сшивка совпадающих узлов (допуск {tolerance})...")
        node_set = self.app.feSet
        node_set.AddAll(7)
        rc = self.app.feCheckCoincidentNode2(node_set.ID, tolerance, True, 1, 1, True, 1, False)
        return rc == -1

    def create_rigid_connections(self):
        print("Создание жестких элементов (RBE2)...")
        try:
            nd = self.app.feNode
            rc, numNode, entID, xyz = nd.GetCoordArray(0)
            if rc != -1: return False

            nodes_dict = {entID[i]: (xyz[3*i], xyz[3*i+1], xyz[3*i+2]) for i in range(numNode)}
            z_min = min(coords[2] for coords in nodes_dict.values())
            z_max = max(coords[2] for coords in nodes_dict.values())
            
            nodes_bottom_cone = dict(filter(lambda element: abs(element[1][2] - z_min) < 1e-7, nodes_dict.items()))
            nodes_top_cone = dict(filter(lambda element: abs(element[1][2] - z_max) < 1e-7, nodes_dict.items()))

            node_obj = self.app.feNode
            self._center_bottom_rbe2_node = node_obj.NextEmptyID()
            node_obj.x, node_obj.y, node_obj.z = 0.0, 0.0, z_min
            node_obj.Put(self._center_bottom_rbe2_node)

            self._center_top_rbe2_node = node_obj.NextEmptyID()
            node_obj.x, node_obj.y, node_obj.z = 0.0, 0.0, z_max
            node_obj.Put(self._center_top_rbe2_node)

            for center_id, dep_nodes, label in [
                (self._center_bottom_rbe2_node, list(nodes_bottom_cone.keys()), "Нижний"),
                (self._center_top_rbe2_node, list(nodes_top_cone.keys()), "Верхний")
            ]:
                if not dep_nodes: continue
                elem = self.app.feElem
                el_id = elem.NextEmptyID()
                elem.type, elem.topology, elem.RigidInterpolate = 29, 13, False
                nodes = list(elem.vnode); nodes[0] = center_id; elem.vnode = nodes
                
                # ГЛАВНЫЙ ШАГ: ХАК ВЫРАВНИВАНИЯ ПАМЯТИ
                correct_vrelease = ((1, 1, 1, 0, 0, 0), (1, 1, 1, 0, 0, 0))
                elem.vrelease = correct_vrelease
                
                dofs_full = [1, 1, 1, 1, 1, 1] * len(dep_nodes)
                elem.PutNodeList(0, len(dep_nodes), dep_nodes, [0]*len(dep_nodes), [1.0]*len(dep_nodes), dofs_full)
                elem.Put(el_id)
            return True
        except: return False

    def apply_loads(self, load_data):
        if not load_data or "axial_force" not in load_data: return None
        force = load_data["axial_force"]
        print(f"Приложение осевой нагрузки {force}...")
        
        ls = self.app.feLoadSet
        self.load_set_id = ls.NextEmptyID()
        ls.title = "Мой набор нагрузок"; ls.Put(self.load_set_id); ls.Active = self.load_set_id

        lm = self.app.feLoadMesh
        lm.SetID = self.load_set_id
        # dof_tuple, values_tuple, func_tuple
        rc = lm.Add(-self._center_top_rbe2_node, 1, 0, (True,True,True), (0.0,0.0,force,0.0,0.0), (0,0,0,0,0))
        return self.load_set_id if rc == -1 else None

    def apply_constraints(self):
        print("Приложение закреплений (6 DOF)...")
        bcs = self.app.feBCSet
        self.constraint_set_id = bcs.NextEmptyID()
        bcs.title = "Fixed Base"; bcs.Put(self.constraint_set_id); bcs.Active = self.constraint_set_id

        bn = self.app.feBCNode
        bn.SetID = self.constraint_set_id
        rc = bn.Add(-self._center_bottom_rbe2_node, True, True, True, True, True, True)
        return self.constraint_set_id if rc == -1 else None

    def setup_analysis(self, load_set_id, constraint_set_id):
        print("Настройка анализа на устойчивость (Buckling)...")
        mgr = self.app.feAnalysisMgr
        am_id = mgr.NextEmptyID()
        mgr.title = "Buckling Analysis"
        mgr.InitAnalysisMgr(36, 7, True)
        mgr.NasModeOn, mgr.NasModeMethod, mgr.NasModeDesiredRoots = True, 6, 1
        
        bc_sets = list(mgr.vBCSet)
        bc_sets[0], bc_sets[2] = constraint_set_id, load_set_id
        mgr.vBCSet = tuple(bc_sets)
        
        mgr.SetOutput(16, -1)
        mgr.Put(am_id); mgr.Active = am_id
        self.app.feFileRebuild(0, True)
        return am_id

    def run_analysis(self, am_id):
        print(f"Запуск решателя для Analysis Set {am_id}...")
        self.app.DialogAutoSkip, self.app.DialogAutoSkipMsg = 1, 1
        try:
            rc = self.app.feAnalysisMgr.Analyze(am_id)
            if rc == -1:
                print("Решатель запущен. Ожидание завершения (25 сек)..."); time.sleep(25)
                return True
            return False
        finally:
            self.app.DialogAutoSkip, self.app.DialogAutoSkipMsg = 0, 0

    def read_results(self):
        """Полная копия метода read_all_results из эталона main.py."""
        print("\n--- Чтение всех результатов ---")
        os_set = self.app.feSet
        os_set.AddAll(28) # 28 = FT_OUT_CASE
        if os_set.Count() == 0:
            print("Результаты не найдены.")
            return None

        set_ids = []
        os_set.Reset()
        while True:
            os_id = os_set.Next()
            if os_id == 0: break
            set_ids.append(os_id)
            os_obj = self.app.feOutputSet
            os_obj.Get(os_id)
            print(f"Найдено набор ID {os_id}: {os_obj.title}")

        elem_set = self.app.feSet
        elem_set.AddAll(8) # FT_ELEM
        rc, count, ent_ids = elem_set.GetArray()
        if rc != -1: return None

        all_results = {}
        actual_vec_id = 7033
        res_obj = self.app.feResults

        for current_set_id in set_ids:
            print(f"\n--- Обработка набора {current_set_id} ---")
            res_obj.clear()
            res_obj.DataNeeded(8, elem_set.ID)

            try:
                # Распаковка (rc, n_added, indices)
                res_call = res_obj.AddColumnV2(current_set_id, actual_vec_id, False)
                if res_call[0] != -1:
                    print(f"Вектор {actual_vec_id} не найден в наборе {current_set_id}.")
                    continue
                column_index = res_call[2][0]
            except Exception as e:
                print(f"Ошибка при вызове AddColumnV2: {e}")
                continue

            if res_obj.Populate() != -1:
                print(f"Нет данных для набора {current_set_id}.")
                continue

            res_data = res_obj.GetScalarAtElemSetV2(column_index, elem_set.ID)
            if res_data[0] == -1 and res_data[1]:
                stress_arr = np.array(res_data[1], dtype=float)
                ids_arr = np.array(ent_ids)
                valid_mask = (stress_arr != 0.0) & (~np.isnan(stress_arr))
                valid_stresses = stress_arr[valid_mask]
                if valid_stresses.size > 0:
                    max_stress = np.max(valid_stresses)
                    print(f"Успешно прочитано {valid_stresses.size} значений.")
                    print(f"МАКСИМАЛЬНОЕ НАПРЯЖЕНИЕ: {max_stress:.2e}")
                    all_results[current_set_id] = dict(zip(ids_arr[valid_mask], valid_stresses))
            else:
                print(f"Не удалось извлечь значения вектора. Код: {res_data[0]}")
        return all_results

    def configure_view(self):
        print("Настройка визуализации вида...")
        surf_set = self.app.feSet; surf_set.AddAll(5)
        self.app.feEntitySetVisibility(5, surf_set.ID, False, True)
        view_obj = self.app.feView; view_obj.Reset()
        while True:
            has_v = view_obj.Next()
            if not has_v: break
            vid = view_obj.ID
            labels = list(view_obj.vLabel); labels[12] = 3; view_obj.vLabel = labels
            view_obj.Put(vid)
            print(f"Вид ID {vid} настроен.")
        self.app.feViewRegenerate(0)
        return True

    def save_model(self, file_path):
        try:
            self.app.feFileSaveAs(0, file_path.replace("/", "\\"))
            self.app.feAppUpdatePanes(True)
        except: pass
