import os
import requests
import json
import logging
from datetime import datetime
from typing import Dict, Optional


class AutoUpdater:
    def __init__(self, gitlab_url: str, project_id: str, token: Optional[str] = None):
        """
        Initialize the auto updater

        Args:
            gitlab_url: Base URL of GitLab instance (e.g., 'https://gitlab.com')
            project_id: GitLab project ID
            token: Optional GitLab access token for private repositories
        """
        self.gitlab_url = gitlab_url.rstrip('/')
        self.project_id = project_id
        self.headers = {'PRIVATE-TOKEN': token} if token else {}
        self.logger = logging.getLogger('harvester.autoupdate')

    def check_for_updates(self, current_version: str) -> Dict:
        """
        Check if updates are available

        Args:
            current_version: Current version of the application

        Returns:
            Dict with update information
        """
        try:
            # Get latest release info from GitLab
            response = requests.get(
                f"{self.gitlab_url}/api/v4/projects/{self.project_id}/releases/permalink/latest",
                headers=self.headers
            )

            if response.status_code == 200:
                release_info = response.json()
                latest_version = release_info['tag_name']

                return {
                    'update_available': latest_version != current_version,
                    'current_version': current_version,
                    'latest_version': latest_version,
                    'release_notes': release_info.get('description', ''),
                    'assets': release_info.get('assets', {}).get('links', [])
                }
            else:
                self.logger.error(f"Failed to check for updates: {response.status_code}")
                return {
                    'update_available': False,
                    'error': 'Failed to check for updates',
                    'current_version': current_version
                }

        except Exception as e:
            self.logger.error(f"Error checking for updates: {str(e)}")
            return {
                'update_available': False,
                'error': str(e),
                'current_version': current_version
            }

    def download_update(self, asset_url: str, destination: str) -> bool:
        """
        Download an update file

        Args:
            asset_url: URL of the update file
            destination: Where to save the file

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(asset_url, headers=self.headers, stream=True)
            if response.status_code == 200:
                with open(destination, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True

        except Exception as e:
            self.logger.error(f"Error downloading update: {str(e)}")

        return False

    def apply_update(self, update_file: str) -> bool:
        """
        Apply the downloaded update

        Args:
            update_file: Path to the downloaded update file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Placeholder for a real update process
            if not os.path.exists(update_file):
                return False

            # TODO: Implement actual update process
            return True

        except Exception as e:
            self.logger.error(f"Error applying update: {str(e)}")
            return False


# Example usage:
if __name__ == '__main__':
    # Initialize updater
    updater = AutoUpdater(
        gitlab_url='https://gitlab.com',
        project_id='your-project-id',
        token='your-optional-token'
    )

    # Check for updates
    update_info = updater.check_for_updates('1.0.0')

    if update_info['update_available']:
        print(f"Update available: {update_info['latest_version']}")

        # Download and apply first asset if available
        if update_info['assets']:
            asset = update_info['assets'][0]
            if updater.download_update(asset['url'], 'update.zip'):
                if updater.apply_update('update.zip'):
                    print("Update successfully applied!")
                else:
                    print("Failed to apply update")
            else:
                print("Failed to download update")
    else:
        print("No updates available")