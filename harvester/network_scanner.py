import nmap
import socket
import subprocess
import json
from typing import Dict, List


class NetworkScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()

    def get_local_ip(self) -> str:
        """Get the local IP address of the current machine."""
        try:
            # Create a temporary socket to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            return f"Error getting IP: {str(e)}"

    def scan_network(self, network: str = None) -> Dict:
        """
        Scan the network and return details about connected devices.

        :param network: Network to scan (e.g., '192.168.1.0/24').
                        If None, uses the local network of the current machine.
        :return: Dictionary with scan results
        """
        if not network:
            # Automatically determine network based on local IP
            local_ip = self.get_local_ip()
            network = f"{'.'.join(local_ip.split('.')[:-1])}.0/24"

        try:
            # Perform network scan
            self.nm.scan(hosts=network, arguments='-sn')

            # Process scan results
            scan_results = {
                'network': network,
                'total_hosts': 0,
                'hosts': []
            }

            for host in self.nm.all_hosts():
                host_info = {
                    'ip': host,
                    'hostname': self.nm[host].hostname(),
                    'status': self.nm[host]['status']['state']
                }
                scan_results['hosts'].append(host_info)
                scan_results['total_hosts'] += 1

            return scan_results

        except Exception as e:
            return {
                'error': str(e),
                'network': network
            }

    def measure_ping_latency(self, target: str = "8.8.8.8", count: int = 5) -> float:
        """
        Measure network latency by pinging a target.

        :param target: IP or hostname to ping
        :param count: Number of ping attempts
        :return: Average ping latency in milliseconds
        """
        try:
            # Use subprocess to run ping command
            output = subprocess.check_output(
                ['ping', '-c', str(count), target],
                universal_newlines=True
            )

            # Extract average latency
            for line in output.split('\n'):
                if 'avg' in line:
                    return float(line.split('/')[-3])

            return -1.0
        except Exception as e:
            return -1.0

    def save_scan_report(self, scan_results: Dict, filename: str = 'network_scan_report.json'):
        """
        Save network scan results to a JSON file.

        :param scan_results: Dictionary of scan results
        :param filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(scan_results, f, indent=4)


# Example usage
if __name__ == '__main__':
    scanner = NetworkScanner()

    # Get local IP
    local_ip = scanner.get_local_ip()
    print(f"Local IP: {local_ip}")

    # Scan network
    scan_results = scanner.scan_network()
    print(json.dumps(scan_results, indent=2))

    # Measure ping latency
    latency = scanner.measure_ping_latency()
    print(f"Average Ping Latency: {latency} ms")

    # Save scan report
    scanner.save_scan_report(scan_results)