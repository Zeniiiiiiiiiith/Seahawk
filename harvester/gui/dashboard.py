import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QProgressBar)
from PyQt5.QtCore import Qt, QTimer
from network_scanner import NetworkScanner
import json


class HarvesterDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scanner = NetworkScanner()
        self.initUI()

        # Start periodic updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(60000)  # Update every minute

        # Initial update
        self.update_dashboard()

    def initUI(self):
        self.setWindowTitle('Seahawks Harvester Dashboard')
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # System Info Section
        sys_info = self.scanner.get_system_info()
        info_widget = QWidget()
        info_layout = QHBoxLayout(info_widget)

        # Left info panel
        left_info = QWidget()
        left_layout = QVBoxLayout(left_info)
        left_layout.addWidget(QLabel(f'Hostname: {sys_info["hostname"]}'))
        left_layout.addWidget(QLabel(f'Local IP: {sys_info["local_ip"]}'))
        left_layout.addWidget(QLabel(f'Platform: {sys_info["platform"]} {sys_info["platform_version"]}'))
        info_layout.addWidget(left_info)

        # Right info panel (latency)
        self.latency_label = QLabel('Network Latency: Measuring...')
        info_layout.addWidget(self.latency_label)

        layout.addWidget(info_widget)

        # Network Scan Section
        scan_widget = QWidget()
        scan_layout = QVBoxLayout(scan_widget)

        # Scan controls
        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget)
        self.scan_button = QPushButton('Start Network Scan')
        self.scan_button.clicked.connect(self.perform_scan)
        control_layout.addWidget(self.scan_button)

        self.scan_progress = QProgressBar()
        self.scan_progress.setVisible(False)
        control_layout.addWidget(self.scan_progress)

        scan_layout.addWidget(control_widget)

        # Scan results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(['IP Address', 'Hostname', 'Status', 'Open Ports'])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        scan_layout.addWidget(self.results_table)

        layout.addWidget(scan_widget)

        # Status bar
        self.statusBar().showMessage('Ready')

    def perform_scan(self):
        """Perform network scan"""
        self.scan_button.setEnabled(False)
        self.scan_progress.setVisible(True)
        self.scan_progress.setRange(0, 0)  # Indeterminate progress
        self.statusBar().showMessage('Scanning network...')

        # Get local network from system info
        sys_info = self.scanner.get_system_info()
        local_ip = sys_info['local_ip']
        network = '.'.join(local_ip.split('.')[:-1]) + '.0/24'

        # Perform scan
        results = self.scanner.scan_network(network)

        # Update results table
        self.results_table.setRowCount(len(results['hosts']))
        for i, host in enumerate(results['hosts']):
            self.results_table.setItem(i, 0, QTableWidgetItem(host['ip']))
            self.results_table.setItem(i, 1, QTableWidgetItem(host.get('hostname', '')))
            self.results_table.setItem(i, 2, QTableWidgetItem(host['status']))

            ports = []
            if 'ports' in host:
                for port in host['ports']:
                    ports.append(f"{port['port']}/{port['protocol']} ({port['service']})")
            self.results_table.setItem(i, 3, QTableWidgetItem(', '.join(ports)))

        self.scan_button.setEnabled(True)
        self.scan_progress.setVisible(False)
        self.statusBar().showMessage(f'Scan complete. Found {results["total_hosts"]} active hosts.')

    def update_dashboard(self):
        """Update dashboard information"""
        # Update latency
        latency = self.scanner.measure_latency()
        if latency:
            self.latency_label.setText(f'Network Latency: {latency:.1f} ms')
        else:
            self.latency_label.setText('Network Latency: Not available')


def main():
    app = QApplication(sys.argv)
    dashboard = HarvesterDashboard()
    dashboard.show()
    sys.exit(app.exec_())