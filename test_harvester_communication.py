# test_harvester_communication.py
import requests
import json
import socket
from datetime import datetime

# Nester server URL
NESTER_URL = 'http://127.0.0.1:8000'

# Step 1: Register probe
print("Registering probe...")
register_data = {
    'name': f'Test-Probe-{socket.gethostname()}',
    'hostname': socket.gethostname(),
    'ip_address': socket.gethostbyname(socket.gethostname()),
    'status': 'online',
    'version': '1.0.0'
}

response = requests.post(
    f'{NESTER_URL}/nester/api/register-probe/',
    json=register_data
)

if response.status_code in (200, 201):
    print("Registration successful!")
    probe_id = response.json()['id']
    print(f"Probe ID: {probe_id}")

    # Step 2: Send scan data
    print("\nSending scan data...")
    scan_data = {
        'scan_time': datetime.now().isoformat(),
        'network': '192.168.1.0/24',
        'total_hosts': 10,
        'hosts': [
            {'ip': '192.168.1.1', 'hostname': 'router', 'status': 'up'},
            {'ip': '192.168.1.2', 'hostname': 'laptop', 'status': 'up'}
        ],
        'latency': 23.5,
        'network_load': 'Normal'
    }

    response = requests.post(
        f'{NESTER_URL}/nester/api/submit-scan/{probe_id}/',
        json=scan_data
    )

    if response.status_code in (200, 201):
        print("Scan data sent successfully!")
        print(response.json())
    else:
        print(f"Failed to send scan data: {response.status_code}")
        print(response.text)

    # Step 3: Send heartbeat
    print("\nSending heartbeat...")
    response = requests.post(
        f'{NESTER_URL}/nester/api/heartbeat/{probe_id}/'
    )

    if response.status_code == 200:
        print("Heartbeat sent successfully!")
    else:
        print(f"Failed to send heartbeat: {response.status_code}")
        print(response.text)
else:
    print(f"Registration failed: {response.status_code}")
    print(response.text)