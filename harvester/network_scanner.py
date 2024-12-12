import nmap
import socket
import psutil
import platform
from datetime import datetime
import subprocess
from typing import Dict, List, Optional


class NetworkScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()

    def get_system_info(self) -> Dict:
        """Get local system information"""
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        return {
            'hostname': hostname,
            'local_ip': local_ip,
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.machine()
        }

    def scan_network(self, target_network: str) -> Dict:
        """
        Perform a network scan using nmap

        Args:
            target_network: Network to scan (e.g., '192.168.1.0/24')
        """
        try:
            # Perform the scan
            self.nm.scan(hosts=target_network, arguments='-sn')

            # Process results
            hosts = []
            total_hosts = 0

            for host in self.nm.all_hosts():
                try:
                    hostname = socket.gethostbyaddr(host)[0]
                except socket.herror:
                    hostname = ''

                host_info = {
                    'ip': host,
                    'hostname': hostname,
                    'status': self.nm[host].state(),
                    'timestamp': datetime.now().isoformat()
                }

                # Add additional port scan for up hosts
                if host_info['status'] == 'up':
                    total_hosts += 1
                    self.nm.scan(host, arguments='-F')  # Fast scan of common ports
                    if host in self.nm.all_hosts():
                        host_info['ports'] = []
                        for proto in self.nm[host].all_protocols():
                            ports = self.nm[host][proto].keys()
                            for port in ports:
                                service = self.nm[host][proto][port]
                                host_info['ports'].append({
                                    'port': port,
                                    'protocol': proto,
                                    'state': service['state'],
                                    'service': service['name']
                                })

                hosts.append(host_info)

            return {
                'scan_time': datetime.now().isoformat(),
                'network': target_network,
                'total_hosts': total_hosts,
                'hosts': hosts
            }

        except Exception as e:
            return {
                'error': str(e),
                'scan_time': datetime.now().isoformat(),
                'network': target_network
            }

    def measure_latency(self, target: str = '8.8.8.8', count: int = 4) -> Optional[float]:
        """Measure network latency to a target"""
        try:
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', str(count), target]
            else:
                cmd = ['ping', '-c', str(count), target]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                # Parse average time from output
                if platform.system().lower() == 'windows':
                    # Windows output parsing
                    for line in result.stdout.split('\n'):
                        if 'Average' in line:
                            return float(line.split('=')[-1].strip('ms '))
                else:
                    # Linux/Unix output parsing
                    for line in result.stdout.split('\n'):
                        if 'avg' in line:
                            return float(line.split('/')[-3])

            return None
        except Exception:
            return None

    def get_network_interfaces(self) -> List[Dict]:
        """Get information about network interfaces"""
        interfaces = []

        for interface, addrs in psutil.net_if_addrs().items():
            interface_info = {
                'name': interface,
                'addresses': []
            }

            for addr in addrs:
                addr_info = {
                    'address': addr.address,
                    'netmask': getattr(addr, 'netmask', None),
                    'family': str(addr.family)
                }
                interface_info['addresses'].append(addr_info)

            interfaces.append(interface_info)

        return interfaces


if __name__ == '__main__':
    # Test the scanner
    scanner = NetworkScanner()

    # Get system info
    print("System Information:")
    print(scanner.get_system_info())

    # Scan local network
    print("\nNetwork Scan:")
    scan_result = scanner.scan_network('192.168.1.0/24')
    print(scan_result)

    # Measure latency
    print("\nNetwork Latency:")
    latency = scanner.measure_latency()
    print(f"Average latency: {latency}ms")