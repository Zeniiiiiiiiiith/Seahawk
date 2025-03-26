from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from ..models import Probe, ProbeData
from .serializers import ProbeSerializer, ProbeDataSerializer


@api_view(['POST'])
def register_probe(request):
    """API endpoint for Harvester to register itself with Nester"""
    serializer = ProbeSerializer(data=request.data)
    if serializer.is_valid():
        probe = serializer.save()
        # Add log entry
        from ..models import MaintenanceLog
        MaintenanceLog.objects.create(
            probe=probe,
            action='Registration',
            details='Probe registered with server',
            status='success'
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def heartbeat(request, probe_id):
    """API endpoint for Harvester to send heartbeat and status updates"""
    try:
        probe = Probe.objects.get(id=probe_id)
        probe.last_contact = timezone.now()
        probe.status = 'online'
        probe.save()
        return Response({'status': 'ok'})
    except Probe.DoesNotExist:
        return Response({'error': 'Probe not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def submit_scan_data(request, probe_id):
    """API endpoint for Harvester to submit network scan results"""
    try:
        probe = Probe.objects.get(id=probe_id)
        data = {
            'probe': probe.id,
            'data_type': 'network_scan',
            'data': request.data,
            'timestamp': timezone.now()
        }
        serializer = ProbeDataSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Probe.DoesNotExist:
        return Response({'error': 'Probe not found'}, status=status.HTTP_404_NOT_FOUND)
