from rest_framework import serializers
from .models import Probe, ProbeData

class ProbeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Probe
        fields = ['id', 'name', 'hostname', 'ip_address', 'status', 'version']

class ProbeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProbeData
        fields = ['probe', 'timestamp', 'data_type', 'data']
        fields = ['probe', 'timestamp', 'data_type', 'data']