import requests
import json
import logging
import socket
import platform
from datetime import datetime
from typing import Dict, Optional


class NesterClient:
    """Client for sending scan data to the Nester server"""

    def __init__(self, nester_url: str, api_key: Optional[str] = None):
        """
        Initialize the Nester client

        Args:
            nester_url: URL of the Nester server (e.g., 'http://nester-server:8000')
            api_key: Optional API key for authentication
        """
        self.nester_url = nester_url.rstrip('/')
        self.headers = {
            'Content-Type': 'application/json'
        }
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'

        self.logger = logging.getLogger('harvester.nester_client')
        self.probe_id = None

    def register_probe(self) -> bool:
        """
        Register this Harvester with the Nester server

        Returns:
            bool: True if registration was successful
        """
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)

            data = {
                'name': f'Probe-{hostname}',
                'hostname': hostname,
                'ip_address': local_ip,
                'status': 'online',
                'version': '1.0.0'  # Should be dynamically determined in production
            }

            response = requests.post(
                f'{self.nester_url}/api/register-probe/',
                headers=self.headers,
                json=data
            )

            if response.status_code in (200, 201):
                response_data = response.json()
                self.probe_id = response_data.get('id')
                self.logger.info(f"Successfully registered with Nester as probe #{self.probe_id}")
                return True
            else:
                self.logger.error(f"Failed to register probe: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Error registering probe: {str(e)}")
            return False

    def send_scan_data(self, scan_results: Dict) -> bool:
        """
        Send network scan results to the Nester server

        Args:
            scan_results: Network scan results

        Returns:
            bool: True if data was successfully sent
        """
        if not self.probe_id:
            self.logger.error("Cannot send scan data: Probe not registered")
            return False

        try:
            # Add timestamp if not present
            if 'scan_time' not in scan_results:
                scan_results['scan_time'] = datetime.now().isoformat()

            response = requests.post(
                f'{self.nester_url}/api/submit-scan/{self.probe_id}/',
                headers=self.headers,
                json=scan_results
            )

            if response.status_code in (200, 201):
                self.logger.info("Successfully sent scan data to Nester")
                return True
            else:
                self.logger.error(f"Failed to send scan data: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Error sending scan data: {str(e)}")
            return False

    def send_heartbeat(self) -> bool:
        """
        Send heartbeat to the Nester server to indicate the probe is active

        Returns:
            bool: True if heartbeat was successfully sent
        """
        if not self.probe_id:
            self.logger.error("Cannot send heartbeat: Probe not registered")
            return False

        try:
            response = requests.post(
                f'{self.nester_url}/api/heartbeat/{self.probe_id}/',
                headers=self.headers
            )

            return response.status_code == 200

        except Exception as e:
            self.logger.error(f"Error sending heartbeat: {str(e)}")
            return False