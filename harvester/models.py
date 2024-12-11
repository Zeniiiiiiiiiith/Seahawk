from django.db import models
from django.utils import timezone


class NetworkScan(models.Model):
    """Stores the results of a network scan"""
    timestamp = models.DateTimeField(default=timezone.now)
    network_address = models.CharField(max_length=50)
    total_hosts = models.IntegerField()
    scan_data = models.JSONField()  # Stores full scan results
    latency = models.FloatField(null=True)  # Network latency in ms

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Scan of {self.network_address} at {self.timestamp}"


class Host(models.Model):
    """Individual hosts discovered during network scans"""
    scan = models.ForeignKey(NetworkScan, on_delete=models.CASCADE, related_name='hosts')
    ip_address = models.GenericIPAddressField()
    hostname = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50)  # e.g., 'up', 'down'
    last_seen = models.DateTimeField(auto_now=True)
    ports = models.JSONField(default=dict)  # Store open ports and services

    def __str__(self):
        return f"{self.ip_address} ({self.hostname})"


class HarvesterConfig(models.Model):
    """Configuration for the Harvester instance"""
    hostname = models.CharField(max_length=255)
    local_ip = models.GenericIPAddressField()
    version = models.CharField(max_length=50)
    last_update = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    scan_interval = models.IntegerField(default=3600)  # seconds
    config_data = models.JSONField(default=dict)  # Additional configuration

    def __str__(self):
        return f"Harvester on {self.hostname} ({self.local_ip})"