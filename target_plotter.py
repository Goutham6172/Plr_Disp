# target_plotter.py
from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtGui import QBrush, Qt
import math

def polar_to_cartesian(r, azimuth):
    angle_rad = math.radians(azimuth)
    x = r * math.sin(angle_rad)
    y = -r * math.cos(angle_rad)
    return x, y

class Target_Plotter:
    def __init__(self, scene):
        self.scene = scene
        self.target_items = []

    def update_targets(self, targets, heading_deg):
        for item in self.target_items:
            self.scene.removeItem(item)
        self.target_items.clear()

        for r, rel_az in targets:
            global_az = (heading_deg + rel_az) % 360
            x, y = polar_to_cartesian(r, global_az)

            dot = QGraphicsEllipseItem(-3, -3, 6, 6)
            dot.setBrush(QBrush(Qt.red))
            dot.setPos(x, y)
            self.scene.addItem(dot)
            self.target_items.append(dot)
