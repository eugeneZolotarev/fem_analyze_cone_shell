import os
import time
import re
import subprocess
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
    def update_property_thickness(self, ppid, thickness): pass
    @abstractmethod
    def build_geometry(self, geom_data): pass
    @abstractmethod
    def build_mesh(self, mesh_data, plate_prop_id): pass
    @abstractmethod
    def build_stringers(self, bpid, h, b, s, s1, s2, sc): pass
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
    def run_analysis(self, am_id): pass
    @abstractmethod
    def export_and_modify_nastran(self, am_id, dat_path, opt_params): pass
    @abstractmethod
    def run_external_nastran(self, dat_path): pass
    @abstractmethod
    def import_nastran_results(self, op2_path): pass
    @abstractmethod
    def get_optimized_thickness(self, dat_path): pass
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
    def __init__(self, params=None):
        self.session = FemapSession()
        self.app = self.session.connect()
        self.params = params or {}
        self.id_generatrix_cone = -1

    def init_new_model(self):
        if not self.app: return False
        try: self.app.feFileNew(); return True
        except: return False

    def create_material(self, m):
        if not self.app: return None
        try:
            mat = self.app.feMatl; mat.title = m["name"]
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

    def update_property_thickness(self, pid, t):
        if not self.app: return False
        prop = self.app.feProp
        if prop.Get(pid) == -1:
            tp = list(prop.pmat); tp[0] = float(t); prop.pmat = tuple(tp)
            return prop.Put(pid) == -1
        return False

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
        surf = self.app.feSurface
        while True:
            sid = s_set.Next()
            if sid == 0: break
            self.app.feMeshAttrSurface(-sid, pid, 0.0); self.app.feMeshApproachSurface(-sid, 3, (0,0,0,0))
            if surf.Get(sid) == -1:
                surf.attrOffsetFrom = 2; surf.Put(sid)
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

    def build_stringers(self, bpid, h, b, s, s1, s2, sc):
        if not self.app or self.id_generatrix_cone <= 0: return False
        cur = self.app.feCurve; cur.Get(self.id_generatrix_cone); p_ids = cur.vStdPoint; p1, p2 = self.app.fePoint, self.app.fePoint; p1.Get(p_ids[0]); p2.Get(p_ids[1])
        A1 = b * s2; A2 = (h - s - s2) * s1; A3 = b * s; A_total = A1 + A2 + A3
        y_c = (A1*(s2/2) + A2*(s2 + (h-s-s2)/2) + A3*(h-s/2)) / A_total
        off_dist_v = -y_c; off_dist_h = -(b-s1)/2
        rc = self.app.feMeshCurve2(-self.id_generatrix_cone, 5, bpid, True, 0, [0,1,0])
        if rc == -1:
            e_set = self.app.feSet; e_set.AddRule(self.id_generatrix_cone, 43)
            tan_v = np.array([p1.x-p2.x, p1.y-p2.y, p1.z-p2.z]); vY = np.array([0,1,0]); vD = np.cross(tan_v, vY); vD /= np.linalg.norm(vD)
            off_v = [float(vD[i] * off_dist_v + vY[i] * off_dist_h) for i in range(3)]
            self.app.feModifyOffsets(e_set.ID, True, True, False, off_v, off_v)
            if sc > 1:
                ct = self.app.feCopyTool; ct.Repetitions = int(sc)-1; ct.RotateAroundVector(8, e_set.ID, [0,0,0], [0,0,1], 360.0/sc, 0.0)
        return True

    def merge_nodes(self, tol=1e-6):
        if not self.app: return False
        n_set = self.app.feSet; n_set.AddAll(7); return self.app.feCheckCoincidentNode2(n_set.ID, tol, True, 1, 1, True, 1, False) == -1

    def create_rigid_connections(self):
        if not self.app: return False
        try:
            nd = self.app.feNode; rc, num, ids, xyz = nd.GetCoordArray(0)
            nodes = {ids[i]: xyz[3*i+2] for i in range(num)}; zmin, zmax = min(nodes.values()), max(nodes.values())
            nb = [i for i, z in nodes.items() if abs(z-zmin)<1e-7]; nt = [i for i, z in nodes.items() if abs(z-zmax)<1e-7]
            n_obj = self.app.feNode
            self._center_bottom_rbe2_node = n_obj.NextEmptyID(); n_obj.x, n_obj.y, n_obj.z = 0, 0, zmin; n_obj.Put(self._center_bottom_rbe2_node)
            self._center_top_rbe2_node = n_obj.NextEmptyID(); n_obj.x, n_obj.y, n_obj.z = 0, 0, zmax; n_obj.Put(self._center_top_rbe2_node)
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
        mgr.NasModeOn, mgr.NasModeMethod = True, 6
        mgr.NasExecAnalyzeFilename = os.path.splitext(os.path.abspath(path))[0]
        bc = list(mgr.vBCSet); bc[0], bc[2] = csid, lsid; mgr.vBCSet = tuple(bc)
        mgr.Put(am_id); mgr.Active = am_id; return am_id

    def run_analysis(self, am_id):
        if not self.app: return False
        self.app.DialogAutoSkip, self.app.DialogAutoSkipMsg = 1, 1
        os_set = self.app.feSet; os_set.AddAll(28); initial = os_set.Count()
        try:
            if self.app.feAnalysisMgr.Analyze(am_id) != -1: return False
            start = time.time()
            while time.time() - start < 300:
                os_set.clear(); os_set.AddAll(28)
                if os_set.Count() > initial: return True
                time.sleep(1.0)
            return False
        finally: self.app.DialogAutoSkip = 0

    def export_and_modify_nastran(self, am_id, dat_path, opt_params):
        if not self.app: return False
        dat_path = os.path.abspath(dat_path)
        self.app.DialogAutoSkip, self.app.DialogAutoSkipMsg = 1, 1
        try:
            rc = self.app.feFileWriteNastran(0, dat_path)
            if rc != -1: return False
        finally: self.app.DialogAutoSkip = 0

        try:
            with open("nastran_opt_template.txt", "r", encoding='utf-8') as f:
                template = f.read().format(bottom_level_thickness_plate=opt_params['t_min'], top_level_thickness_plate=opt_params['t_max'], stress_limit_material=opt_params['sigma_y'])
            with open(dat_path, "r", encoding='utf-8') as f: original_lines = f.readlines()
            new_content = template + "\n" + "".join(original_lines[35:])
            with open(dat_path, "w", encoding='utf-8') as f: f.write(new_content)
            return True
        except: return False

    def _wait_for_f06(self, f06_path):
        start_wait = time.time()
        while time.time() - start_wait < 600:
            if os.path.exists(f06_path):
                try:
                    with open(f06_path, "r", encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if "END OF JOB" in content: return True
                        if "FATAL ERROR" in content: return False
                except: pass
            time.sleep(1.0)
        return False

    def run_external_nastran(self, dat_path):
        if not self.app: return False
        nastran_exe = self.params.get('nastran_path')
        if not nastran_exe: return False
        dat_dir, dat_filename = os.path.dirname(os.path.abspath(dat_path)), os.path.basename(dat_path)
        log_file = os.path.splitext(os.path.abspath(dat_path))[0] + ".f06"
        if os.path.exists(log_file):
            try: os.remove(log_file)
            except: pass
        args = [nastran_exe, dat_filename, "bat=no", "old=no", "scr=yes"]
        try:
            subprocess.Popen(args, cwd=dat_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return self._wait_for_f06(log_file)
        except: return False

    def import_nastran_results(self, op2_path):
        if not self.app or not os.path.exists(op2_path): return False
        rc = self.app.feFileReadNastranResults(0, os.path.abspath(op2_path))
        return rc == -1

    def get_optimized_thickness(self, dat_path):
        csv_path = os.path.splitext(os.path.abspath(dat_path))[0] + "_sol200.csv"
        if not os.path.exists(csv_path): return 0.0
        try:
            with open(csv_path, "r", encoding='utf-8') as f: lines = f.readlines()
            in_dvid_section, last_value = False, 0.0
            for line in lines:
                if "DVID" in line and "1" in line: in_dvid_section = True; continue
                if in_dvid_section:
                    if "End of Data" in line: break
                    parts = line.strip().split(",")
                    if len(parts) >= 2:
                        try: last_value = float(parts[1])
                        except: pass
            return last_value
        except: return 0.0

    def read_results(self):
        if not self.app: return {"max_stress": 0, "eigenvalue": 0, "beam_max_stress": 0}
        os_s = self.app.feSet; os_s.clear(); os_s.AddAll(28); os_s.Reset(); set_ids = []
        while True:
            oid = os_s.Next()
            if oid == 0: break
            set_ids.append(oid)
        
        if len(set_ids) < 1: return {"max_stress": 0, "eigenvalue": 0, "beam_max_stress": 0}
        
        static_id = buckling_id = -1
        os_obj = self.app.feOutputSet
        for sid in reversed(set_ids):
            if os_obj.Get(sid) == -1:
                title = os_obj.title
                if "Eigenvalue" in title and buckling_id == -1: buckling_id = sid
                elif ("Static" in title or "Case 1" in title) and static_id == -1: static_id = sid
        
        if static_id == -1: static_id = set_ids[-1]
        
        ev = 0.0
        if buckling_id != -1:
            os_obj.Get(buckling_id)
            match = re.search(r"Eigenvalue\s+\d+\s+([\d.]+)", os_obj.title)
            if match: ev = float(match.group(1))
        
        res = self.app.feResults; el_set = self.app.feSet; el_set.clear(); el_set.AddAll(8)
        max_p_s = 0.0; res.clear(); res.DataNeeded(8, el_set.ID)
        rc, n, idx = res.AddColumnV2(static_id, 7033, False)
        if rc == -1:
            res.Populate(); rc_v, val = res.GetScalarAtElemSetV2(idx[0], el_set.ID)
            if rc_v == -1 and val:
                v = np.array(val); v = v[np.isfinite(v) & (v > 0)]
                if v.size > 0: max_p_s = float(max(v))
        
        max_b_s = 0.0; res.clear(); res.DataNeeded(8, el_set.ID)
        rc, n, idx = res.AddColumnV2(static_id, 3164, False)
        if rc == -1:
            res.Populate(); rc_v, val = res.GetScalarAtElemSetV2(idx[0], el_set.ID)
            if rc_v == -1 and val:
                v = np.abs(np.array(val)); v = v[np.isfinite(v)]
                if v.size > 0: max_b_s = float(max(v))
        return {"max_stress": max_p_s, "eigenvalue": ev, "beam_max_stress": max_b_s}

    def configure_view(self):
        v = self.app.feView; v.Reset()
        while v.Next():
            l = list(v.vLabel); l[12] = 3; v.vLabel = l; v.Put(v.ID)
        self.app.feViewRegenerate(0); return True
    def save_model(self, path): 
        if self.app: self.app.feFileSaveAs(0, os.path.abspath(path))
    def close_model(self): 
        if self.app: self.app.feFileClose(False)
    def delete_model_file(self, path):
        models_dir = os.path.dirname(os.path.abspath(path)); time.sleep(1.5)
        if os.path.exists(models_dir):
            for f in os.listdir(models_dir):
                fp = os.path.join(models_dir, f); 
                try: 
                    if os.path.isfile(fp): os.unlink(fp)
                    elif os.path.isdir(fp): shutil.rmtree(fp)
                except: pass
