import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Seahawk.settings')
django.setup()

# Now we can import Django models and our harvester code
from harvester.network_scanner import NetworkScanner


def test_network_scanner():
    """Test the NetworkScanner functionality"""
    print("=== Testing NetworkScanner ===")
    scanner = NetworkScanner()

    # Get system info
    print("\n1. System Information:")
    system_info = scanner.get_system_info()
    for key, value in system_info.items():
        print(f"  {key}: {value}")

    # Test network interfaces
    print("\n2. Network Interfaces:")
    interfaces = scanner.get_network_interfaces()
    for interface in interfaces[:3]:  # Show first 3 interfaces
        print(f"  Interface: {interface['name']}")
        for addr in interface['addresses'][:2]:  # Show first 2 addresses per interface
            print(f"    {addr.get('family', 'Unknown')}: {addr.get('address', 'Unknown')}")

    # Test latency
    print("\n3. Network Latency:")
    latency = scanner.measure_latency()
    print(f"  Latency to 8.8.8.8: {latency} ms")

    # Perform a limited network scan (just a few IPs to be quick)
    print("\n4. Limited Network Scan:")
    local_ip = system_info['local_ip']
    base_ip = '.'.join(local_ip.split('.')[:3])
    scan_range = f"{base_ip}.1-5"  # Scan only first 5 IPs in the subnet

    print(f"  Scanning {scan_range}...")
    try:
        scan_results = scanner.scan_network(scan_range)
        print(f"  Found {scan_results.get('total_hosts', 0)} hosts")
        for host in scan_results.get('hosts', []):
            print(f"    Host: {host.get('ip', 'Unknown')} ({host.get('hostname', 'Unknown')})")
            print(f"    Status: {host.get('status', 'Unknown')}")
    except Exception as e:
        print(f"  Error scanning network: {str(e)}")


if __name__ == "__main__":
    test_network_scanner()