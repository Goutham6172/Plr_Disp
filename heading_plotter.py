# heading_plotter.py
from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtGui import QPen, Qt
import math

def polar_to_cartesian(r, azimuth):
    angle_rad = math.radians(azimuth)
    x = r * math.sin(angle_rad)
    y = -r * math.cos(angle_rad)
    return x, y

class Heading_Plotter:
    def __init__(self, scene):
        self.scene = scene
        self.arrow = None

    def update_heading(self, heading_deg):
        if self.arrow:
            self.scene.removeItem(self.arrow)
        x, y = polar_to_cartesian(80, heading_deg)
        self.arrow = QGraphicsLineItem(0, 0, x, y)
        self.arrow.setPen(QPen(Qt.blue, 3))
        self.scene.addItem(self.arrow)
