import os
import time
import traceback
import threading
import shutil
import re
import numpy as np
import pythoncom
from abc import ABC, abstractmethod
from session import FemapSession

class ModelBuilder(ABC):
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
    def setup_analysis(self, load_set_id, constraint_set_id, model_path): pass
    @abstractmethod
    def run_analysis(self, am_id, model_path): pass
    @abstractmethod
    def read_results(self): pass
    @abstractmethod
    def configure_view(self): pass
    @abstractmethod
    def save_model(self, file_path): pass
    @abstractmethod
    def close_model(self): pass
    @abstractmethod
    def delete_model_file(self, file_path): pass

class ConeModelBuilder(ModelBuilder):
    def __init__(self):
        self.session = FemapSession()
        self.app = self.session.connect()
        self._analysis_finished_event = threading.Event()
        self._center_bottom_rbe2_node = -1
        self._center_top_rbe2_node = -1

    def notify_analysis_finished(self):
        self._analysis_finished_event.set()

    def init_new_model(self):
        if not self.app: return False
        try:
            self.app.feFileNew()
            time.sleep(0.5); return True
        except: return False

    def create_material(self, m):
        if not self.app: return None
        try:
            mat = self.app.feMatl; mat.title = m["name"]; mat.type = 0
            mat.Ex, mat.Nuxy, mat.Density = float(m["E"]), float(m["nu"]), float(m["rho"])
            mid = mat.NextEmptyID(); mat.Put(mid); return mid
        except: return None

    def create_property(self, p, mid):
        if not self.app: return None
        try:
            prop = self.app.feProp; prop.title = p["name"]; prop.matlID = mid
            if p["type"].lower() == "plate":
                prop.type = 17; tp = list(prop.pmat); tp[0] = float(p["thickness"]); prop.pmat = tuple(tp)
            elif p["type"].lower() == "beam_z":
                prop.type = 5; d = p["dimensions"]
                d_list = (float(d["h"]), float(d["w_top"]), float(d["w_bot"]), float(d["t_top"]), float(d["t_bot"]), float(d["t_web"]))
                tf = list(prop.vflagI); tf[1], tf[2] = 13, 1; prop.vflagI = tf; prop.ComputeStdShape2(True, 13, d_list, 0, 1, True, True, True)
                tp = list(prop.pmat); tp[40], tp[41], tp[42], tp[43], tp[44], tp[45] = d_list; prop.pmat = tp
            pid = prop.NextEmptyID(); prop.Put(pid); return pid
        except: return None

    def build_geometry(self, g):
        if not self.app: return False
        try:
            sz = [float(g["diameter_big"])/2, float(g["diameter_small"])/2, float(g["height"])]
            self.app.feSolidPrimitive(0, 3, True, [0,0,0], sz, "Cone")
            s = self.app.feSet; s.Add(1); self.app.feSolidExplode(s.ID)
            self.app.feDelete(39, -3); self.app.feDelete(39, -4); return True
        except: return False

    def build_mesh(self, m, pid):
        if not self.app: return False
        nc, nh = int(m["divisions_circular"]), int(m["divisions_height"])
        s_set = self.app.feSet; s_set.AddAll(5); s_set.Reset()
        while True:
            sid = s_set.Next()
            if sid == 0: break
            self.app.feMeshAttrSurface(-sid, pid, 0.0); self.app.feMeshApproachSurface(-sid, 3, (0,0,0,0))
            c_set = self.app.feSet; c_set.AddRule(sid, 8); c_set.Reset()
            while True:
                cid = c_set.Next()
                if cid == 0: break
                cur = self.app.feCurve; cur.Get(cid); is_c = cur.IsArc() == -1
                if not is_c:
                    p1, p2 = self.app.fePoint, self.app.fePoint; p_ids = cur.vStdPoint; p1.Get(p_ids[0]); p2.Get(p_ids[1])
                    if abs(p1.z - p2.z) < 1e-6: is_c = True
                    else: self.id_generatrix_cone = cid
                nd = (nc // 2) if is_c else nh
                self.app.feMeshSizeCurve(-cid, nd, 0.0, 0, 0, 0, 0, 0, 1.0, 0, True)
            self.app.feMeshSurface2(-sid, pid, 4, True, False)
        return True

    def build_stringers(self, bpid, bh, pt, bw, btw, sc):
        if not self.app or self.id_generatrix_cone <= 0: return False
        cur = self.app.feCurve; cur.Get(self.id_generatrix_cone); p_ids = cur.vStdPoint; p1, p2 = self.app.fePoint, self.app.fePoint; p1.Get(p_ids[0]); p2.Get(p_ids[1])
        rc = self.app.feMeshCurve2(-self.id_generatrix_cone, 5, bpid, True, 0, [0,1,0])
        if rc == -1:
            e_set = self.app.feSet; e_set.AddRule(self.id_generatrix_cone, 43)
            tan_v = np.array([p1.x-p2.x, p1.y-p2.y, p1.z-p2.z]); vY = np.array([0,1,0]); vD = np.cross(tan_v, vY); vD /= np.linalg.norm(vD)
            off_v = [float(vD[i]*( - (bh + pt) / 2) + vY[i]*( - (bw - btw) / 2)) for i in range(3)]
            self.app.feModifyOffsets(e_set.ID, True, True, False, off_v, off_v)
            if sc > 1:
                ct = self.app.feCopyTool; ct.Repetitions = int(sc)-1; ct.RotateAroundVector(8, e_set.ID, [0,0,0], [0,0,1], 360.0/sc, 0.0)
        return True

    def merge_nodes(self, tol=1e-6):
        if not self.app: return False
        n_set = self.app.feSet; n_set.AddAll(7); return self.app.feCheckCoincidentNode2(n_set.ID, tol, True, 1, 1, True, 1, False) == -1

    def create_rigid_connections(self):
        if not self.app: return False
        print("Создание жестких элементов (RBE2)...")
        try:
            nd = self.app.feNode; rc, num, ids, xyz = nd.GetCoordArray(0)
            nodes = {ids[i]: xyz[3*i+2] for i in range(num)}; zmin, zmax = min(nodes.values()), max(nodes.values())
            nb = [i for i, z in nodes.items() if abs(z-zmin)<1e-7]; nt = [i for i, z in nodes.items() if abs(z-zmax)<1e-7]
            n_obj = self.app.feNode
            self._center_bottom_rbe2_node = n_obj.NextEmptyID(); n_obj.x = 0.0; n_obj.y = 0.0; n_obj.z = zmin; n_obj.Put(self._center_bottom_rbe2_node)
            self._center_top_rbe2_node = n_obj.NextEmptyID(); n_obj.x = 0.0; n_obj.y = 0.0; n_obj.z = zmax; n_obj.Put(self._center_top_rbe2_node)
            for cid, dep in [(self._center_bottom_rbe2_node, nb), (self._center_top_rbe2_node, nt)]:
                el = self.app.feElem; el.type, el.topology, el.RigidInterpolate = 29, 13, False
                vn = list(el.vnode); vn[0] = cid; el.vnode = vn; el.vrelease = ((1,1,1,0,0,0),(1,1,1,0,0,0))
                el.PutNodeList(0, len(dep), dep, [0]*len(dep), [1.0]*len(dep), [1]*6*len(dep)); el.Put(el.NextEmptyID())
            return True
        except: return False

    def apply_loads(self, ld):
        if not self.app: return None
        ls = self.app.feLoadSet; lsid = ls.NextEmptyID(); ls.Put(lsid); ls.Active = lsid
        lm = self.app.feLoadMesh; lm.SetID = lsid; rc = lm.Add(-self._center_top_rbe2_node, 1, 0, (True,True,True), (0,0,ld["axial_force"],0,0), (0,0,0,0,0))
        return lsid if rc == -1 else None

    def apply_constraints(self):
        if not self.app: return None
        bc = self.app.feBCSet; csid = bc.NextEmptyID(); bc.Put(csid); bc.Active = csid
        bn = self.app.feBCNode; bn.SetID = csid; rc = bn.Add(-self._center_bottom_rbe2_node, True, True, True, True, True, True)
        return csid if rc == -1 else None

    def setup_analysis(self, lsid, csid, path):
        if not self.app: return None
        mgr = self.app.feAnalysisMgr; am_id = mgr.NextEmptyID(); mgr.InitAnalysisMgr(36, 7, True)
        mgr.NasModeOn, mgr.NasModeMethod, mgr.NasModeDesiredRoots = True, 6, 1
        mgr.NasExecAnalyzeFilename = os.path.basename(path).replace(".modfem", "")
        bc = list(mgr.vBCSet); bc[0], bc[2] = csid, lsid; mgr.vBCSet = tuple(bc)
        mgr.SetOutput(16, -1); mgr.Put(am_id); mgr.Active = am_id; return am_id

    def run_analysis(self, amid, path):
        if not self.app: return False
        self.app.DialogAutoSkip, self.app.DialogAutoSkipMsg = 1, 1
        os_set = self.app.feSet; os_set.AddAll(28); initial = os_set.Count()
        try:
            if self.app.feAnalysisMgr.Analyze(amid) != -1: return False
            start = time.time()
            while time.time() - start < 300:
                os_set.clear(); os_set.AddAll(28)
                if os_set.Count() > initial: return True
                time.sleep(1.0)
            return False
        finally: self.app.DialogAutoSkip = 0

    def read_results(self):
        """Считывает напряжения из Set 1 (Статика) и Eigenvalue из Set 2 (Устойчивость)."""
        if not self.app: return {"max_stress": 0.0, "eigenvalue": 0.0}
        
        os = self.app.feSet; os.AddAll(28); os.Reset()
        set_ids = []
        while True:
            oid = os.Next()
            if oid == 0: break
            set_ids.append(oid)
            
        if len(set_ids) < 2:
            print("ПРЕДУПРЕЖДЕНИЕ: Найдено менее 2-х наборов результатов. Проверьте расчет.")
            # Если набор всего один, попробуем извлечь из него хоть что-то
            static_id = set_ids[0] if set_ids else 0
            buckling_id = 0
        else:
            # СТРОГАЯ ЛОГИКА SOL 105:
            static_id = set_ids[0]   # Первый набор - статика (Pre-buckling)
            buckling_id = set_ids[1] # Второй набор - первая мода (Buckling Mode 1)

        # 1. Извлекаем Eigenvalue из набора Устойчивости (buckling_id)
        eigenvalue = 0.0
        if buckling_id > 0:
            os_obj = self.app.feOutputSet; os_obj.Get(buckling_id)
            match = re.search(r"Eigenvalue\s+\d+\s+([\d.]+)", os_obj.title)
            if match:
                try: eigenvalue = float(match.group(1))
                except: pass

        # 2. Извлекаем Max Von Mises из набора Статики (static_id)
        max_stress = 0.0
        if static_id > 0:
            el_set = self.app.feSet; el_set.AddAll(8)
            res = self.app.feResults; res.clear(); res.DataNeeded(8, el_set.ID)
            # Вектор 7033 - Plate Top Von Mises
            rc, n, idx = res.AddColumnV2(static_id, 7033, False)
            if rc == -1:
                res.Populate(); rc, val = res.GetScalarAtElemSetV2(idx[0], el_set.ID)
                if rc == -1 and val:
                    # Фильтруем нули и NaN для чистоты результата
                    arr = np.array(val)
                    valid = arr[np.isfinite(arr) & (arr > 0)]
                    if valid.size > 0: max_stress = float(np.max(valid))

        return {"max_stress": max_stress, "eigenvalue": eigenvalue}

    def configure_view(self):
        if not self.app: return False
        v = self.app.feView; v.Reset()
        while v.Next():
            l = list(v.vLabel); l[12] = 3; v.vLabel = l; v.Put(v.ID)
        self.app.feViewRegenerate(0); return True

    def save_model(self, path): 
        if self.app: self.app.feFileSaveAs(0, path.replace("/", "\\"))

    def close_model(self): 
        if self.app: self.app.feFileClose(False)
    
    def delete_model_file(self, path):
        models_dir = os.path.dirname(path)
        print(f"Полная очистка папки: {models_dir}")
        time.sleep(1.5)
        if os.path.exists(models_dir):
            for filename in os.listdir(models_dir):
                file_path = os.path.join(models_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path): os.unlink(file_path)
                    elif os.path.isdir(file_path): shutil.rmtree(file_path)
                except: pass
