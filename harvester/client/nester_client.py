import requests
import socket
import json
from datetime import datetime
import logging
from typing import Dict, Optional


class NesterClient:
    def __init__(self, nester_url: str, api_key: Optional[str] = None):
        """
        Initialize connection to Nester server

        Args:
            nester_url: URL of the Nester server (e.g., 'https://nester.nfl-it.com')
            api_key: Optional API key for authentication
        """
        self.nester_url = nester_url.rstrip('/')
        self.api_key = api_key
        self.probe_id = None
        self.logger = logging.getLogger('harvester.nester_client')

    def get_headers(self) -> Dict:
        """Get headers for API requests"""
        headers = {
            'Content-Type': 'application/json'
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers

    def register_probe(self) -> bool:
        """Register this Harvester with the Nester server"""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)

            data = {
                'name': f'Probe-{hostname}',
                'hostname': hostname,
                'ip_address': local_ip,
                'status': 'online',
                'version': '1.0.0'
            }

            response = requests.post(
                f'{self.nester_url}/api/register-probe/',
                headers=self.get_headers(),
                json=data
            )

            if response.status_code == 201:
                self.probe_id = response.json()['id']
                return True
            else:
                self.logger.error(f"Failed to register probe: {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Error registering probe: {str(e)}")
            return False

    def submit_scan_data(self, scan_results: Dict) -> bool:
        """Submit network scan results to Nester"""
        if not self.probe_id:
            self.logger.error("Probe not registered")
            return False

        try:
            response = requests.post(
                f'{self.nester_url}/api/submit-scan/{self.probe_id}/',
                headers=self.get_headers(),
                json=scan_results
            )

            return response.status_code == 201

        except Exception as e:
            self.logger.error(f"Error submitting scan data: {str(e)}")
            return False

    def send_heartbeat(self) -> bool:
        """Send heartbeat to Nester to indicate probe is alive"""
        if not self.probe_id:
            return False

        try:
            response = requests.post(
                f'{self.nester_url}/api/heartbeat/{self.probe_id}/',
                headers=self.get_headers()
            )

            return response.status_code == 200

        except Exception as e:
            self.logger.error(f"Error sending heartbeat: {str(e)}")
            return False