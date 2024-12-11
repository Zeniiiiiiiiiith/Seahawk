from django.urls import path
from . import views

app_name = 'nester'

urlpatterns = [
    path('', views.ProbeListView.as_view(), name='probe-list'),
    path('probe/<int:pk>/', views.ProbeDetailView.as_view(), name='probe-detail'),
    path('probe/<int:pk>/dashboard/', views.probe_dashboard, name='probe-dashboard'),
    path('probe/<int:pk>/status/', views.probe_status_api, name='probe-status'),
    path('probe/<int:pk>/scan-report/', views.scan_report, name='scan-report'),
    path('alerts/', views.alerts_view, name='alerts'),
    path('system-status/<int:pk>/', views.system_status, name='system-status'),
]