# # target_plotter.py
# from PySide6.QtWidgets import QGraphicsEllipseItem
# from PySide6.QtGui import QBrush, Qt
# import math

# def polar_to_cartesian(r, azimuth):
#     angle_rad = math.radians(azimuth)
#     x = r * math.sin(angle_rad)
#     y = -r * math.cos(angle_rad)
#     return x, y

# class Target_Plotter:
#     def __init__(self, scene):
#         self.scene = scene
#         self.target_items = []

#     def update_targets(self, targets, heading_deg):
#         for item in self.target_items:
#             self.scene.removeItem(item)
#         self.target_items.clear()

#         for r, rel_az in targets:
#             global_az = (heading_deg + rel_az) % 360
#             x, y = polar_to_cartesian(r, global_az)

#             dot = QGraphicsEllipseItem(-3, -3, 6, 6)
#             dot.setBrush(QBrush(Qt.red))
#             dot.setPos(x, y)
#             self.scene.addItem(dot)
#             self.target_items.append(dot)

from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtGui import QBrush
from PySide6.QtCore import QPointF, Qt
import math
from collections import defaultdict, deque

class Target_Plotter:
    def __init__(self, scene):
        self.scene = scene
        self.max_trail_length = 20
        self.targets = {}  # target_id -> QGraphicsEllipseItem (current position)
        self.history = defaultdict(lambda: deque(maxlen=self.max_trail_length))  # target_id -> deque[(x, y)]
        self.trails = defaultdict(list)  # target_id -> list of trail dots (QGraphicsEllipseItem)
        self.trail_enabled = True
        self.active_target_id = None  # None = all trails visible

    def update_targets(self, targets):
        # targets = list of (target_id, range, azimuth)
        current_ids = set()

        for idx, (r, az) in enumerate(targets):
            target_id = idx  # Use index as temporary ID

            angle_rad = math.radians(az)
            x = r * math.sin(angle_rad)
            y = -r * math.cos(angle_rad)  # Invert y for Qt

            current_ids.add(target_id)
            self.history[target_id].append((x, y))

            # Update or create target dot
            if target_id not in self.targets:
                dot = QGraphicsEllipseItem(-4, -4, 8, 8)
                dot.setBrush(QBrush(Qt.green))
                dot.setZValue(1)
                self.scene.addItem(dot)
                self.targets[target_id] = dot

            self.targets[target_id].setPos(QPointF(x, y))

        # Remove vanished targets
        for tid in list(self.targets.keys()):
            if tid not in current_ids:
                self.scene.removeItem(self.targets[tid])
                for item in self.trails[tid]:
                    self.scene.removeItem(item)
                del self.targets[tid]
                del self.history[tid]
                del self.trails[tid]

        # Draw trails
        if self.trail_enabled:
            self._draw_trails()

    def _draw_trails(self):
        # Clear old trail dots
        for tid, items in self.trails.items():
            for item in items:
                self.scene.removeItem(item)
        self.trails.clear()

        for tid, points in self.history.items():
            if self.active_target_id is not None and tid != self.active_target_id:
                continue  # show only selected target's trail

            self.trails[tid] = []
            for i, (x, y) in enumerate(points):
                dot = QGraphicsEllipseItem(-2, -2, 4, 4)
                dot.setPos(QPointF(x, y))
                opacity = 0.2 + 0.6 * (i / self.max_trail_length)
                dot.setBrush(QBrush(Qt.green))
                dot.setOpacity(opacity)
                dot.setZValue(0)
                self.scene.addItem(dot)
                self.trails[tid].append(dot)

    def set_trail_enabled(self, enabled: bool):
        self.trail_enabled = enabled
        if not enabled:
            # remove all trails visually
            for items in self.trails.values():
                for item in items:
                    self.scene.removeItem(item)
            self.trails.clear()
        else:
            self._draw_trails()

    def focus_on_target(self, target_id: int):
        self.active_target_id = target_id
        if self.trail_enabled:
            self._draw_trails()

    def clear_focus(self):
        self.active_target_id = None
        if self.trail_enabled:
            self._draw_trails()
