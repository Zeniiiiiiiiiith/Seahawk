# settings_harvester.py
DEBUG = False
ALLOWED_HOSTS = ['*']  # Or specific IP of the harvester VM

# Nester server configuration
NESTER_URL = 'http://nester-server-ip'  # Replace with actual Nester IP
NESTER_API_KEY = 'your-api-key'  # Replace with actual API key

# Network scanning configuration
SCAN_INTERVAL = 3600  # 1 hour between scans
HEARTBEAT_INTERVAL = 300  # 5 minutes between heartbeats