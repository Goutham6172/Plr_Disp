# mainwindow.py
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow
from PySide6.QtCore import Qt
from target_plotter import TargetPlotter
from heading_plotter import HeadingPlotter
from radar_controller import RadarController
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Radar Polar Display")
        self.resize(800, 800)

        # Setup scene and view
        self.scene = QGraphicsScene(-300, -300, 600, 600)
        self.view = QGraphicsView(self.scene)
        self.view.scale(1, -1)  # North-up (y-axis flipped)
        self.setCentralWidget(self.view)

        # Draw reference axes
        self.scene.addLine(-300, 0, 300, 0)
        self.scene.addLine(0, -300, 0, 300)

        # Initialize plotting components
        self.target_plotter = TargetPlotter(self.scene)
        self.heading_plotter = HeadingPlotter(self.scene)

        # Controller: handles incoming data and updates plots
        self.controller = RadarController(self.target_plotter, self.heading_plotter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
