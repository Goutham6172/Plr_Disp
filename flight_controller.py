# flight_controller.py
from PySide6.QtCore import QObject, QDataStream, QIODevice, QByteArray
from PySide6.QtNetwork import QTcpSocket, QHostAddress, QUdpSocket
import struct, bisect, time
from collections import deque

class Flight_Controller(QObject):
    def __init__(self, target_plotter, heading_plotter):
        super().__init__()
        self.target_plotter = target_plotter
        self.heading_plotter = heading_plotter
        self.heading_history = deque(maxlen=100)  # list of (timestamp_ms, heading)
        self.tcp_buffer = b''

        # --- TCP Socket for target data ---
        self.tcp_socket = QTcpSocket(self)
        self.tcp_socket.readyRead.connect(self.handle_tcp_data)
        self.tcp_socket.connected.connect(lambda: print("[TCP] Connected to server"))
        self.tcp_socket.errorOccurred.connect(lambda e: print(f"[TCP Error] {e}"))

        # Connect to TCP server
        self.tcp_socket.connectToHost(QHostAddress("0.0.0.0"), 5002) # update port and ip

        # --- UDP Socket for heading updates ---
        self.udp_socket = QUdpSocket(self)
        self.udp_socket.bind(QHostAddress("127.0.0.1"), 5001)  # update port
        self.udp_socket.readyRead.connect(self.handle_udp_data)

    def handle_udp_data(self):
        while self.udp_socket.hasPendingDatagrams():
            datagram, _, _ = self.udp_socket.readDatagram(12)
            if len(datagram) == 12:
                heading, timestamp = struct.unpack('fQ', datagram)
                self.heading_history.append((timestamp, heading))
                self.heading_plotter.update_heading(heading)

    def find_nearest_heading(self, timestamp):
        times = [ts for ts, _ in self.heading_history]
        idx = bisect.bisect_left(times, timestamp)
        if idx == 0:
            return self.heading_history[0][1]
        elif idx >= len(times):
            return self.heading_history[-1][1]
        else:
            before = self.heading_history[idx - 1]
            after = self.heading_history[idx]
            # Return the closer one
            return before[1] if (timestamp - before[0]) < (after[0] - timestamp) else after[1]

    def handle_tcp_data(self):
        self.tcp_buffer += self.tcp_socket.readAll().data()
        while len(self.tcp_buffer) >= 16:
            r, az_rel, timestamp = struct.unpack('ffQ', self.tcp_buffer[:16])
            self.tcp_buffer = self.tcp_buffer[16:]

            heading = self.find_nearest_heading(timestamp)
            self.target_plotter.update_targets([(r, az_rel)], heading)
