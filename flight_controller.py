# flight_controller.py
from PySide6.QtCore import QObject, QDataStream, QIODevice, QByteArray
from PySide6.QtNetwork import QTcpSocket, QHostAddress, QUdpSocket
import struct

class Flight_Controller(QObject):
    def __init__(self, target_plotter, heading_plotter):
        super().__init__()
        self.target_plotter = target_plotter
        self.heading_plotter = heading_plotter
        self.current_heading = 0
        self.targets = []

        # --- TCP Socket for target data ---
        self.tcp_socket = QTcpSocket(self)
        self.tcp_socket.readyRead.connect(self.handle_tcp_data)
        self.tcp_socket.connected.connect(lambda: print("[TCP] Connected to server"))
        self.tcp_socket.errorOccurred.connect(lambda e: print(f"[TCP Error] {e}"))

        # Connect to TCP server
        self.tcp_socket.connectToHost(QHostAddress("127.0.0.1"), 5000) # update port and ip

        # --- UDP Socket for heading updates ---
        self.udp_socket = QUdpSocket(self)
        self.udp_socket.bind(QHostAddress.AnyIPv4, 5001)  # update port
        self.udp_socket.readyRead.connect(self.handle_udp_data)

    def handle_udp_data(self):
        while self.udp_socket.hasPendingDatagrams():
            datagram, _, _ = self.udp_socket.readDatagram(4)
            if len(datagram) != 4:
                continue
            self.current_heading = struct.unpack('f', datagram)[0]
            self.heading_plotter.update_heading(self.current_heading)

    def handle_tcp_data(self):
        while self.tcp_socket.bytesAvailable() >= 8:
            data = self.tcp_socket.read(8)  # 2 floats: range and rel_az
            if len(data) != 8:
                continue
            r, rel_az = struct.unpack('ff', data)
            self.targets.append((r, rel_az))

        # After receiving all, update plot
        if self.targets:
            self.target_plotter.update_targets(self.targets, self.current_heading)
            self.targets.clear()
