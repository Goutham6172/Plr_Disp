# radar_controller.py
from PySide6.QtCore import QObject, QTimer

class Flight_Controller(QObject):
    def __init__(self, target_plotter, heading_plotter):
        super().__init__()
        self.target_plotter = target_plotter
        self.heading_plotter = heading_plotter
        self.current_heading = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.simulate_data)
        self.timer.start(1000)

    def simulate_data(self):
        # Simulated heading update from UDP
        self.current_heading = (self.current_heading + 30) % 360
        self.heading_plotter.update_heading(self.current_heading)

        # Simulated target data from TCP (range, relative azimuth)
        targets = [
            (100, 0),
            (120, 45),
            (140, -30)
        ]
        self.target_plotter.update_targets(targets, self.current_heading)
