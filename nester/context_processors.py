from .models import Probe, Alert


def footer_context(request):
    """Add common footer data to all templates"""
    return {
        'active_probes': Probe.objects.filter(status='online').count(),
        'active_alerts': Alert.objects.filter(status='active').count(),
        'recent_alerts': Alert.objects.filter(status='active').order_by('-timestamp')[:5],  # 5 most recent alerts
    }