from django.db import models
from django.utils import timezone


class NetworkScanResult(models.Model):
    """Store results of network scans"""
    timestamp = models.DateTimeField(default=timezone.now)
    network_address = models.CharField(max_length=50)
    total_hosts = models.IntegerField()
    scan_data = models.JSONField()  # Full scan results
    latency = models.FloatField(null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Scan at {self.timestamp}"


class DiscoveredHost(models.Model):
    """Individual hosts found during scans"""
    ip_address = models.GenericIPAddressField()
    hostname = models.CharField(max_length=255, blank=True)
    mac_address = models.CharField(max_length=17, blank=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    open_ports = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.ip_address} ({self.hostname})"


class HarvesterConfig(models.Model):
    """Harvester configuration and status"""
    hostname = models.CharField(max_length=255)
    local_ip = models.GenericIPAddressField()
    version = models.CharField(max_length=50)
    last_update_check = models.DateTimeField(null=True)
    last_successful_scan = models.DateTimeField(null=True)
    scan_interval = models.IntegerField(default=3600)  # seconds
    is_scanning = models.BooleanField(default=False)
    gitlab_repo = models.URLField(
        max_length=255,
        default='https://gitlab.com/nfl-it/seahawks-monitoring.git'
    )
    gitlab_branch = models.CharField(max_length=50, default='main')

    def __str__(self):
        return f"Harvester on {self.hostname}"