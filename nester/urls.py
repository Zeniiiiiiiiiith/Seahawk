from django.urls import path
from . import views
from .api import views as api_views

app_name = 'nester'

urlpatterns = [
    # Web interface URLs
    path('', views.ProbeListView.as_view(), name='probe-list'),
    path('probe/<int:pk>/', views.ProbeDetailView.as_view(), name='probe-detail'),
    path('probe/<int:pk>/dashboard/', views.probe_dashboard, name='probe-dashboard'),
    path('probe/<int:pk>/status/', views.probe_status_api, name='probe-status'),
    path('probe/<int:pk>/scan-report/', views.scan_report, name='scan-report'),
    path('alerts/', views.alerts_view, name='alerts'),
    path('system-status/<int:pk>/', views.system_status, name='system-status'),

    # API endpoints for Harvester communication
    path('api/register-probe/', api_views.register_probe, name='api-register-probe'),
    path('api/submit-scan/<int:probe_id>/', api_views.submit_scan_data, name='api-submit-scan'),
    path('api/heartbeat/<int:probe_id>/', api_views.heartbeat, name='api-heartbeat'),
]
