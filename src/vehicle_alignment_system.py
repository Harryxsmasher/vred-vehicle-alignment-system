# ----------------------------------------------------------
# CONFIG
# ----------------------------------------------------------
 
TRACKER = "tracker-1"      # <-- Only ONE tracker now
 
VEHICLE_NODE = "U171_1"
STEERING_REF = "STEERING"
 
PRESET_FILE = "offset_preset.json"
 
 
# ----------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------
 
from PySide2 import QtWidgets, QtCore
from PySide6.QtGui import QVector4D, QVector3D, QMatrix4x4, QQuaternion
import json
import os
 
 
# ----------------------------------------------------------
# GLOBAL OFFSETS
# ----------------------------------------------------------
 
MODEL_OFFSET_X = 0.0
MODEL_OFFSET_Y = 0.0
MODEL_OFFSET_Z = 0.0
 
MODEL_ROT_X = 0.0
MODEL_ROT_Y = 0.0
MODEL_ROT_Z = 0.0
 
 
# ----------------------------------------------------------
# MATRIX HELPERS
# ----------------------------------------------------------
 
def extractRotationMatrix(m4: QMatrix4x4):
    r0 = m4.row(0)
    r1 = m4.row(1)
    r2 = m4.row(2)
    return QMatrix4x4(
        r0.x(), r0.y(), r0.z(), 0,
        r1.x(), r1.y(), r1.z(), 0,
        r2.x(), r2.y(), r2.z(), 0,
        0,      0,      0,      1
    )
 
def eulerXYZ_to_quaternion(rx, ry, rz):
    return QQuaternion.fromEulerAngles(rx, ry, rz)
 
 
# ----------------------------------------------------------
# INITIAL SETUP
# ----------------------------------------------------------
 
vehicleNode  = vrNodeService.findNode(VEHICLE_NODE)
steeringNode = vrNodeService.findNode(STEERING_REF)
 
vehicleMat = vehicleNode.getWorldTransform()
steerMat   = steeringNode.getWorldTransform()
 
vpos = vehicleMat.column(3)
spos = steerMat.column(3)
 
OFFSET = QVector4D(
    spos.x() - vpos.x(),
    spos.y() - vpos.y(),
    spos.z() - vpos.z(),
    1
)
 
invVehicle = QMatrix4x4(vehicleMat.data())
invVehicle = invVehicle.inverted()[0]
 
pivot3 = QVector3D(spos.x(), spos.y(), spos.z())
pivotLocal3 = invVehicle.map(pivot3)
pivotLocal = QVector4D(pivotLocal3.x(), pivotLocal3.y(), pivotLocal3.z(), 1)
 
 
# ----------------------------------------------------------
# ANNOTATION SETUP
# ----------------------------------------------------------
 
annotation = vrAnnotationService.createAnnotation("Tracker Live Annotation")
annotation.setText("Tracking Position...")
 
 
# ----------------------------------------------------------
# VEHICLE UPDATER (ONE TRACKER)
# ----------------------------------------------------------
 
class VehicleUpdater(vrAEBase):
 
    def __init__(self):
        vrAEBase.__init__(self)
        self.addLoop()
 
    def loop(self):
        global MODEL_OFFSET_X, MODEL_OFFSET_Y, MODEL_OFFSET_Z
        global MODEL_ROT_X, MODEL_ROT_Y, MODEL_ROT_Z
 
        dev = vrDeviceService.getVRDevice(TRACKER)
        if not dev:
            return
 
        node = dev.getNode()
        if not node:
            return
 
        # --- POSITION ---
        mat = node.getWorldTransform()
        p = mat.column(3)
 
        basePos = QVector4D(
            p.x() - OFFSET.x(),
            p.y() - OFFSET.y(),
            p.z() - OFFSET.z(),
            1
        )
 
        # Apply manual translation offsets
        basePos.setX(basePos.x() + MODEL_OFFSET_X)
        basePos.setY(basePos.y() + MODEL_OFFSET_Y)
        basePos.setZ(basePos.z() + MODEL_OFFSET_Z)
 
        # --- ROTATION ---
        trackerRotMat = extractRotationMatrix(mat)
 
        # Optional: fix upside‑down controller/tracker
        flipQuat = QQuaternion.fromEulerAngles(180.0, 0.0, 0.0)
        flipMat = QMatrix4x4()
        flipMat.rotate(flipQuat)
        trackerRotMat = trackerRotMat * flipMat
 
        # Manual axis offsets
        manualQuat = eulerXYZ_to_quaternion(
            MODEL_ROT_X, MODEL_ROT_Y, MODEL_ROT_Z
        )
        manualRotMat = QMatrix4x4()
        manualRotMat.rotate(manualQuat)
 
        # final rotation = tracker rotation × manual rotation
        finalRotMat = trackerRotMat * manualRotMat
 
        # --- APPLY TO VEHICLE ---
        M = QMatrix4x4()
        M.translate(pivotLocal.x(), pivotLocal.y(), pivotLocal.z())
        M = M * finalRotMat
        M.translate(-pivotLocal.x(), -pivotLocal.y(), -pivotLocal.z())
        M.setColumn(3, basePos)
 
        vehicleNode.setWorldTransform(M)
 
        # Annotation update
        annotation.setPosition(QVector3D(p.x(), p.y(), p.z()))
        annotation.setText(f"Tracker Pos:\nX={p.x():.2f}\nY={p.y():.2f}\nZ={p.z():.2f}")
 
 
updater = VehicleUpdater()
 
 
# ----------------------------------------------------------
# GUI WINDOW
# ----------------------------------------------------------
 
class OffsetGUI(QtWidgets.QWidget):
 
    def __init__(self):
        super().__init__()
 
        self.setWindowTitle("Vehicle Offset Controls")
        self.setMinimumWidth(400)
 
        layout = QtWidgets.QVBoxLayout()
 
        # ---- POSITION SLIDERS ----
 
        def make_slider(label, callback):
            row = QtWidgets.QHBoxLayout()
            lbl = QtWidgets.QLabel(label)
            valbox = QtWidgets.QLineEdit("0.0")
            valbox.setFixedWidth(70)
 
            slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            slider.setMinimum(-4000)
            slider.setMaximum(4000)
            slider.setValue(0)
 
            def on_slider_change(value):
                f = value / 10.0
                valbox.setText(f"{f:.2f}")
                callback(f)
 
            def on_text_change():
                try:
                    f = float(valbox.text())
                    callback(f)
                except:
                    pass
 
            slider.valueChanged.connect(on_slider_change)
            valbox.editingFinished.connect(on_text_change)
 
            row.addWidget(lbl)
            row.addWidget(slider)
            row.addWidget(valbox)
            return row
 
        layout.addLayout(make_slider("Offset X", self.set_x))
        layout.addLayout(make_slider("Offset Y", self.set_y))
        layout.addLayout(make_slider("Offset Z", self.set_z))
 
        # ---- ROTATION BUTTON GROUP ----
 
        def make_rotation_row(label, getter, setter):
            wrapper = QtWidgets.QVBoxLayout()
 
            top = QtWidgets.QHBoxLayout()
            lbl = QtWidgets.QLabel(label)
            valbox = QtWidgets.QLineEdit("0.0")
            valbox.setFixedWidth(70)
 
            def on_text():
                try:
                    val = float(valbox.text())
                    setter(val)
                except:
                    pass
 
            valbox.editingFinished.connect(on_text)
 
            top.addWidget(lbl)
            top.addWidget(valbox)
            wrapper.addLayout(top)
 
            btnRow = QtWidgets.QHBoxLayout()
 
            def addBtn(text, delta):
                btn = QtWidgets.QPushButton(text)
                btn.setFixedWidth(50)
 
                def act():
                    val = getter() + delta
                    setter(val)
                    valbox.setText(f"{val:.2f}")
 
                btn.clicked.connect(act)
                return btn
 
            for text, delta in [
                ("+0.1", 0.1), ("-0.1", -0.1),
                ("+1", 1), ("-1", -1),
                ("+10", 10), ("-10", -10),
            ]:
                btnRow.addWidget(addBtn(text, delta))
 
            wrapper.addLayout(btnRow)
            return wrapper
 
        layout.addLayout(make_rotation_row("Rot X", lambda: MODEL_ROT_X, self.set_rot_x))
        layout.addLayout(make_rotation_row("Rot Y", lambda: MODEL_ROT_Y, self.set_rot_y))
        layout.addLayout(make_rotation_row("Rot Z", lambda: MODEL_ROT_Z, self.set_rot_z))
 
        # ---- PRESET SAVE/LOAD ----
 
        saveBtn = QtWidgets.QPushButton("Save Preset")
        loadBtn = QtWidgets.QPushButton("Load Preset")
 
        saveBtn.clicked.connect(self.save_preset)
        loadBtn.clicked.connect(self.load_preset)
 
        layout.addWidget(saveBtn)
        layout.addWidget(loadBtn)
 
        self.setLayout(layout)
        self.show()
 
    # ---------------- OFFSET CALLBACKS -----------------
 
    def set_x(self, v):  global MODEL_OFFSET_X; MODEL_OFFSET_X = v
    def set_y(self, v):  global MODEL_OFFSET_Y; MODEL_OFFSET_Y = v
    def set_z(self, v):  global MODEL_OFFSET_Z; MODEL_OFFSET_Z = v
 
    def set_rot_x(self, v):  global MODEL_ROT_X; MODEL_ROT_X = v
    def set_rot_y(self, v):  global MODEL_ROT_Y; MODEL_ROT_Y = v
    def set_rot_z(self, v):  global MODEL_ROT_Z; MODEL_ROT_Z = v
 
    # ---------------- PRESET SAVE/LOAD -----------------
 
    def save_preset(self):
        data = {
            "x": MODEL_OFFSET_X,
            "y": MODEL_OFFSET_Y,
            "z": MODEL_OFFSET_Z,
            "rx": MODEL_ROT_X,
            "ry": MODEL_ROT_Y,
            "rz": MODEL_ROT_Z
        }
        with open(PRESET_FILE, "w") as f:
            json.dump(data, f, indent=4)
        print("Preset saved:", data)
 
    def load_preset(self):
        global MODEL_OFFSET_X, MODEL_OFFSET_Y, MODEL_OFFSET_Z
        global MODEL_ROT_X, MODEL_ROT_Y, MODEL_ROT_Z
 
        if not os.path.exists(PRESET_FILE):
            print("No preset file found.")
            return
 
        with open(PRESET_FILE, "r") as f:
            data = json.load(f)
 
        MODEL_OFFSET_X = data["x"]
        MODEL_OFFSET_Y = data["y"]
        MODEL_OFFSET_Z = data["z"]
        MODEL_ROT_X = data["rx"]
        MODEL_ROT_Y = data["ry"]
        MODEL_ROT_Z = data["rz"]
 
        print("Preset loaded:", data)
 
 
gui = OffsetGUI()