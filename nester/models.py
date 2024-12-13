from django.db import models
from django.utils import timezone


class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('warning', 'Warning'),
        ('info', 'Information'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('resolved', 'Resolved'),
    ]

    probe = models.ForeignKey('Probe', on_delete=models.CASCADE, related_name='alerts')
    timestamp = models.DateTimeField(default=timezone.now)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    message = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts'
    )

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_severity_display()} Alert - {self.message}"

    def resolve(self, user=None):
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.save()


class AlertSettings(models.Model):
    cpu_threshold = models.IntegerField(default=80)
    memory_threshold = models.IntegerField(default=80)
    disk_threshold = models.IntegerField(default=90)
    latency_threshold = models.IntegerField(default=1000)
    retention_days = models.IntegerField(default=30)
    email_critical = models.BooleanField(default=True)
    email_warnings = models.BooleanField(default=False)

    def __str__(self):
        return "Alert Settings"


class Probe(models.Model):
    """Represents a Harvester probe in the field"""
    name = models.CharField(max_length=255)
    hostname = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    status = models.CharField(max_length=50, default='offline')  # online/offline
    last_contact = models.DateTimeField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    version = models.CharField(max_length=50)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.status})"

    def is_online(self):
        """Check if probe has contacted server recently"""
        if not self.last_contact:
            return False
        return (timezone.now() - self.last_contact).seconds < 300  # 5 minutes threshold


class ProbeData(models.Model):
    """Stores data received from probes"""
    probe = models.ForeignKey(Probe, on_delete=models.CASCADE, related_name='data_points')
    timestamp = models.DateTimeField(default=timezone.now)
    data_type = models.CharField(max_length=50)  # e.g., 'network_scan', 'system_status'
    data = models.JSONField()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.probe.name} - {self.data_type} at {self.timestamp}"


class MaintenanceLog(models.Model):
    """Log of maintenance activities"""
    probe = models.ForeignKey(Probe, on_delete=models.CASCADE, related_name='maintenance_logs')
    timestamp = models.DateTimeField(default=timezone.now)
    action = models.CharField(max_length=100)  # e.g., 'update', 'restart'
    details = models.TextField()
    status = models.CharField(max_length=50)  # success/failed

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.probe.name} - {self.action} ({self.status})"