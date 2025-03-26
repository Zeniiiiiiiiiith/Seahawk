import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QProgressBar)
from PyQt5.QtCore import Qt, QTimer
from ..network_scanner import NetworkScanner
from ..client.nester_client import NesterClient
import os
import json
import logging


class HarvesterDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scanner = NetworkScanner()

        # Initialize Nester client
        nester_url = os.environ.get('NESTER_URL', 'http://localhost:8000')
        api_key = os.environ.get('NESTER_API_KEY', '')
        self.nester_client = NesterClient(nester_url, api_key)

        # Register with Nester
        self.registered = self.nester_client.register_probe()

        self.initUI()

        # Start periodic updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(60000)  # Update every minute

        # Start heartbeat timer
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self.send_heartbeat)
        self.heartbeat_timer.start(300000)  # Send heartbeat every 5 minutes

        # Initial update
        self.update_dashboard()

    # Add this method to send heartbeat
    def send_heartbeat(self):
        """Send heartbeat to Nester server"""
        if self.registered:
            success = self.nester_client.send_heartbeat()
            if success:
                self.statusBar().showMessage('Heartbeat sent to Nester', 2000)
            else:
                self.statusBar().showMessage('Failed to send heartbeat', 2000)

    # Update the perform_scan method to send data to Nester
    def perform_scan(self):
        """Perform network scan and send results to Nester"""
        try:
            self.scan_button.setEnabled(False)
            self.scan_progress.setVisible(True)
            self.scan_progress.setRange(0, 0)  # Indeterminate progress
            self.statusBar().showMessage('Scanning network...')

            # Get local network from system info
            sys_info = self.scanner.get_system_info()
            local_ip = sys_info['local_ip']

            # For testing, scan a wider range
            network_base = '.'.join(local_ip.split('.')[:-1])
            network = f"{network_base}.0/24"  # Use CIDR notation for better nmap scanning

            self.statusBar().showMessage(f'Scanning network {network}...')

            try:
                # Perform the scan
                self.scanner.nm.scan(hosts=network, arguments='-sP -T4')  # Fast ping scan

                # Process results
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

                # Update the results table
                self.results_table.setRowCount(len(hosts))

                for i, host in enumerate(hosts):
                    self.results_table.setItem(i, 0, QTableWidgetItem(host['ip']))
                    self.results_table.setItem(i, 1, QTableWidgetItem(host['hostname']))
                    self.results_table.setItem(i, 2, QTableWidgetItem(host['status']))
                    self.results_table.setItem(i, 3, QTableWidgetItem("N/A"))

                # Prepare scan results for Nester
                scan_results = {
                    'scan_time': datetime.now().isoformat(),
                    'network': network,
                    'total_hosts': total_hosts,
                    'hosts': hosts,
                    'latency': self.scanner.measure_latency() or -1,
                    'network_load': 'Normal'  # Could be calculated based on metrics
                }

                # Send to Nester if registered
                if self.registered:
                    sent = self.nester_client.send_scan_data(scan_results)
                    if sent:
                        self.statusBar().showMessage(
                            f'Scan complete. Found {total_hosts} active hosts. Data sent to Nester.')
                    else:
                        self.statusBar().showMessage(
                            f'Scan complete. Found {total_hosts} active hosts. Failed to send data to Nester.')
                else:
                    self.statusBar().showMessage(
                        f'Scan complete. Found {total_hosts} active hosts. (Not registered with Nester)')

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
