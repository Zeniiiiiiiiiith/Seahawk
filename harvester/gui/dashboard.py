import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QProgressBar)
from PyQt5.QtCore import Qt, QTimer
from ..network_scanner import NetworkScanner
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
        """Perform network scan with more reliable approach"""
        try:
            self.scan_button.setEnabled(False)
            self.scan_progress.setVisible(True)
            self.scan_progress.setRange(0, 0)  # Indeterminate progress
            self.statusBar().showMessage('Scanning network...')

            # Get local network from system info
            sys_info = self.scanner.get_system_info()
            local_ip = sys_info['local_ip']

            # For testing, use a wider range (first 20 addresses in your subnet)
            network_base = '.'.join(local_ip.split('.')[:-1])
            network = f"{network_base}.0/24"  # Use CIDR notation for better nmap scanning

            self.statusBar().showMessage(f'Scanning network {network}...')

            # When scanning with nmap, use more aggressive options
            try:
                # Replace this with direct network scanning if scanner method doesn't work
                self.scanner.nm.scan(hosts=network, arguments='-sP -T4')  # Fast ping scan

                # Process results directly from nmap
                hosts = []
                total_hosts = 0

                for host in self.scanner.nm.all_hosts():
                    if self.scanner.nm[host].state() == 'up':
                        total_hosts += 1
                        host_info = {
                            'ip': host,
                            'hostname': self.scanner.nm[host].hostname(),
                            'status': 'up'
                        }
                        hosts.append(host_info)

                # Clear and update the table
                self.results_table.setRowCount(len(hosts))

                for i, host in enumerate(hosts):
                    self.results_table.setItem(i, 0, QTableWidgetItem(host['ip']))
                    self.results_table.setItem(i, 1, QTableWidgetItem(host['hostname']))
                    self.results_table.setItem(i, 2, QTableWidgetItem(host['status']))

                    # For now, just add a placeholder for ports
                    self.results_table.setItem(i, 3, QTableWidgetItem("N/A"))

                self.statusBar().showMessage(f'Scan complete. Found {total_hosts} active hosts.')

            except Exception as e:
                self.statusBar().showMessage(f'Error during scan: {str(e)}')

        except Exception as e:
            self.statusBar().showMessage(f'Error preparing scan: {str(e)}')
        finally:
            self.scan_button.setEnabled(True)
            self.scan_progress.setVisible(False)

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


if __name__ == "__main__":
    main()
