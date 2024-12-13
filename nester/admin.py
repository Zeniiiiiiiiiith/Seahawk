from django.contrib import admin
from .models import Probe, ProbeData, MaintenanceLog, Alert, AlertSettings


@admin.register(Probe)
class ProbeAdmin(admin.ModelAdmin):
    list_display = ('name', 'hostname', 'ip_address', 'status', 'last_contact', 'version')
    list_filter = ('status',)
    search_fields = ('name', 'hostname', 'ip_address')


@admin.register(ProbeData)
class ProbeDataAdmin(admin.ModelAdmin):
    list_display = ('probe', 'data_type', 'timestamp')
    list_filter = ('data_type', 'probe')


@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ('probe', 'action', 'timestamp', 'status')
    list_filter = ('status', 'action')


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('probe', 'severity', 'status', 'message', 'timestamp')
    list_filter = ('severity', 'status')


@admin.register(AlertSettings)
class AlertSettingsAdmin(admin.ModelAdmin):
    list_display = ('cpu_threshold', 'memory_threshold', 'disk_threshold')