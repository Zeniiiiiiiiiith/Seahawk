import sys
import os
import time
import json
import logging
import argparse
import threading
from datetime import datetime

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QProgressBar)
from PyQt5.QtCore import Qt, QTimer

from harvester.network_scanner import NetworkScanner
from harvester.client.nester_client import NesterClient

# Configure logging
logger = logging.getLogger('harvester')


class HarvesterDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scanner = NetworkScanner()

        # Initialize Nester client
        nester_url = os.environ.get('NESTER_URL', 'http://localhost:8000/nester')
        api_key = os.environ.get('API_KEY', '')
        self.nester_client = NesterClient(nester_url, api_key)

        # Try to register with Nester
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

        # Show registration status
        if self.registered:
            self.statusBar().showMessage(f'Registered with Nester as probe #{self.nester_client.probe_id}')
        else:
            self.statusBar().showMessage('Not registered with Nester server')

    def update_dashboard(self):
        """Update dashboard information"""
        # Update latency
        latency = self.scanner.measure_latency()
        if latency:
            self.latency_label.setText(f'Network Latency: {latency:.1f} ms')
        else:
            self.latency_label.setText('Network Latency: Not available')

    def send_heartbeat(self):
        """Send heartbeat to Nester server"""
        if self.registered:
            success = self.nester_client.send_heartbeat()
            if success:
                self.statusBar().showMessage('Heartbeat sent to Nester', 2000)
            else:
                self.statusBar().showMessage('Failed to send heartbeat', 2000)

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
                    'network_load': 'Normal'
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
                logger.error(f'Error during scan: {str(e)}')

        except Exception as e:
            self.statusBar().showMessage(f'Error preparing scan: {str(e)}')
            logger.error(f'Error preparing scan: {str(e)}')
        finally:
            self.scan_button.setEnabled(True)
            self.scan_progress.setVisible(False)


# CLI mode functionality
def run_cli_mode():
    """Run harvester in CLI mode without GUI"""
    parser = argparse.ArgumentParser(description='Seahawks Harvester')
    parser.add_argument('--nester-url', default=os.environ.get('NESTER_URL', 'http://localhost:8000/nester'),
                        help='URL of the Nester server')
    parser.add_argument('--api-key', default=os.environ.get('API_KEY', ''),
                        help='API key for Nester authentication')
    parser.add_argument('--scan-interval', type=int, default=int(os.environ.get('SCAN_INTERVAL', '3600')),
                        help='Interval between scans in seconds')
    parser.add_argument('--heartbeat-interval', type=int, default=int(os.environ.get('HEARTBEAT_INTERVAL', '300')),
                        help='Interval between heartbeats in seconds')
    parser.add_argument('--daemon', action='store_true',
                        help='Run as a daemon service')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

    logger.info("Starting Seahawks Harvester in CLI mode")

    # Initialize components
    scanner = NetworkScanner()
    nester_client = NesterClient(args.nester_url, args.api_key)

    # Register with Nester
    logger.info(f"Registering with Nester server at {args.nester_url}")
    registered = nester_client.register_probe()
    if not registered:
        logger.error("Failed to register with Nester server. Exiting.")
        sys.exit(1)

    logger.info(f"Successfully registered as probe #{nester_client.probe_id}")

    # Define scan function
    def perform_scan():
        try:
            logger.info("Starting network scan...")
            sys_info = scanner.get_system_info()
            local_ip = sys_info['local_ip']
            network = '.'.join(local_ip.split('.')[:-1]) + '.0/24'

            logger.info(f"Scanning network {network}")

            # Perform scan
            scanner.nm.scan(hosts=network, arguments='-sP -T4')

            hosts = []
            total_hosts = 0

            for host in scanner.nm.all_hosts():
                if scanner.nm[host].state() == 'up':
                    total_hosts += 1
                    host_info = {
                        'ip': host,
                        'hostname': scanner.nm[host].hostname(),
                        'status': 'up'
                    }
                    hosts.append(host_info)
                    logger.debug(f"Found host: {host}")

            # Prepare scan results
            scan_results = {
                'scan_time': datetime.now().isoformat(),
                'network': network,
                'total_hosts': total_hosts,
                'hosts': hosts,
                'latency': scanner.measure_latency() or -1,
                'network_load': 'Normal'
            }

            logger.info(f"Scan complete. Found {total_hosts} active hosts.")

            # Send to Nester
            sent = nester_client.send_scan_data(scan_results)
            if sent:
                logger.info("Scan data sent to Nester successfully.")
            else:
                logger.error("Failed to send scan data to Nester.")

        except Exception as e:
            logger.error(f"Error during scan: {str(e)}", exc_info=True)

    # Define heartbeat function
    def send_heartbeat():
        try:
            logger.info("Sending heartbeat to Nester")
            success = nester_client.send_heartbeat()
            if success:
                logger.info("Heartbeat sent successfully")
            else:
                logger.error("Failed to send heartbeat")
        except Exception as e:
            logger.error(f"Error sending heartbeat: {str(e)}", exc_info=True)

    # Run initial scan
    perform_scan()
    send_heartbeat()

    if args.daemon:
        logger.info(
            f"Running in daemon mode. Scan every {args.scan_interval}s, Heartbeat every {args.heartbeat_interval}s")

        # Schedule regular scans
        scan_timer = None
        heartbeat_timer = None

        while True:
            try:
                # Sleep between operations
                time.sleep(1)

                # Check if scan timer is due
                current_time = time.time()
                if scan_timer is None or current_time - scan_timer >= args.scan_interval:
                    scan_thread = threading.Thread(target=perform_scan)
                    scan_thread.daemon = True
                    scan_thread.start()
                    scan_timer = current_time

                # Check if heartbeat timer is due
                if heartbeat_timer is None or current_time - heartbeat_timer >= args.heartbeat_interval:
                    heartbeat_thread = threading.Thread(target=send_heartbeat)
                    heartbeat_thread.daemon = True
                    heartbeat_thread.start()
                    heartbeat_timer = current_time

            except KeyboardInterrupt:
                logger.info("Received interrupt, shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}", exc_info=True)
                time.sleep(10)  # Wait a bit before retrying
    else:
        logger.info("One-time scan completed. Exiting.")


def main():
    """Entry point for the application"""
    if '--cli' in sys.argv or os.environ.get('HARVESTER_MODE', '').lower() == 'cli':
        run_cli_mode()
    else:
        app = QApplication(sys.argv)
        dashboard = HarvesterDashboard()
        dashboard.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
