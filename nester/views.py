from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.utils import timezone
from .models import Probe, ProbeData, MaintenanceLog
from django.shortcuts import render
from .models import Alert, AlertSettings


class ProbeListView(ListView):
    """Display list of all probes"""
    model = Probe
    template_name = 'nester/probe_list.html'
    context_object_name = 'probes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_probes'] = Probe.objects.filter(status='online').count()
        context['total_probes'] = Probe.objects.count()
        return context


class ProbeDetailView(DetailView):
    """Display detailed information about a specific probe"""
    model = Probe
    template_name = 'nester/probe_detail.html'
    context_object_name = 'probe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        probe = self.get_object()
        context['latest_scan'] = probe.data_points.filter(
            data_type='network_scan'
        ).first()
        context['maintenance_logs'] = probe.maintenance_logs.all()[:5]
        return context


def probe_dashboard(request, pk):
    """Display real-time dashboard for a specific probe"""
    probe = get_object_or_404(Probe, pk=pk)

    # Get latest scan data
    latest_scan = ProbeData.objects.filter(
        probe=probe,
        data_type='network_scan'
    ).first()

    # Get recent activity logs
    recent_logs = MaintenanceLog.objects.filter(
        probe=probe
    ).order_by('-timestamp')[:5]

    return render(request, 'nester/probe_dashboard.html', {
        'probe': probe,
        'latest_scan': latest_scan,
        'recent_logs': recent_logs,
    })


def probe_status_api(request, pk):
    """API endpoint for getting probe status"""
    probe = get_object_or_404(Probe, pk=pk)
    return JsonResponse({
        'status': probe.status,
        'last_contact': probe.last_contact.isoformat() if probe.last_contact else None,
        'is_online': probe.is_online(),
        'version': probe.version,
    })


def scan_report(request, pk):
    """Display latest network scan report for a probe"""
    probe = get_object_or_404(Probe, pk=pk)
    latest_scan = ProbeData.objects.filter(
        probe=probe,
        data_type='network_scan'
    ).first()

    return render(request, 'nester/scan_report.html', {
        'probe': probe,
        'scan_data': latest_scan.data if latest_scan else None,
        'scan_time': latest_scan.timestamp if latest_scan else None,
    })


def system_status(request, pk):
    """Display system status for a specific probe"""
    probe = get_object_or_404(Probe, pk=pk)
    latest_data = ProbeData.objects.filter(
        probe=probe,
        data_type='system_status'
    ).first()

    return render(request, 'nester/system_status.html', {
        'probe': probe,
        'system_stats': latest_data.data if latest_data else None,
    })


def alerts_view(request):
    """Display system alerts"""
    # Get all alerts, ordered by timestamp (most recent first)
    alerts = Alert.objects.all().order_by('-timestamp')

    # Count alerts by severity
    alert_counts = {
        'critical': Alert.objects.filter(severity='critical', status='active').count(),
        'warning': Alert.objects.filter(severity='warning', status='active').count(),
        'info': Alert.objects.filter(severity='info', status='active').count(),
        'resolved': Alert.objects.filter(status='resolved').count(),
    }

    context = {
        'alerts': alerts,
        'alert_counts': alert_counts,
        'alert_settings': AlertSettings.objects.first(),  # Get global alert settings
    }

    return render(request, 'nester/alerts.html', context)