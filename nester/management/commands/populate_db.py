from django.core.management.base import BaseCommand
from django.utils import timezone
from nester.models import Probe, ProbeData, Alert, AlertSettings, MaintenanceLog
import random
import datetime


class Command(BaseCommand):
    help = 'Populates the database with test data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')

        # Create alert settings if they don't exist
        if not AlertSettings.objects.exists():
            AlertSettings.objects.create(
                cpu_threshold=80,
                memory_threshold=85,
                disk_threshold=90,
                latency_threshold=200,
                retention_days=30,
                email_critical=True,
                email_warnings=False
            )
            self.stdout.write(self.style.SUCCESS('Created alert settings'))

        # Create test probes
        probe_data = [
            {
                'name': 'Seattle Seahawks',
                'hostname': 'seahawks-server',
                'ip_address': '192.168.1.10',
                'status': 'online',
                'version': '1.2.0',
            },
            {
                'name': 'Kansas City Chiefs',
                'hostname': 'chiefs-server',
                'ip_address': '192.168.1.11',
                'status': 'online',
                'version': '1.1.5',
            },
            {
                'name': 'San Francisco 49ers',
                'hostname': '49ers-server',
                'ip_address': '192.168.1.12',
                'status': 'offline',
                'version': '1.2.0',
            },
            {
                'name': 'Dallas Cowboys',
                'hostname': 'cowboys-server',
                'ip_address': '192.168.1.13',
                'status': 'online',
                'version': '1.0.9',
            },
        ]

        probes = []
        for data in probe_data:
            probe, created = Probe.objects.get_or_create(
                name=data['name'],
                defaults={
                    'hostname': data['hostname'],
                    'ip_address': data['ip_address'],
                    'status': data['status'],
                    'version': data['version'],
                    'last_contact': timezone.now() if data['status'] == 'online' else None
                }
            )
            probes.append(probe)
            if created:
                self.stdout.write(f'Created probe: {probe.name}')
            else:
                self.stdout.write(f'Probe already exists: {probe.name}')

        # Create scan data for each probe
        for probe in probes:
            # Skip offline probes
            if probe.status == 'offline':
                continue

            # Create network scan data
            scan_data = {
                'scan_time': timezone.now().isoformat(),
                'network': '192.168.1.0/24',
                'total_hosts': random.randint(10, 30),
                'active_hosts': random.randint(5, 10),
                'hosts': [
                    {
                        'ip': '192.168.1.1',
                        'hostname': 'gateway',
                        'status': 'up',
                        'ports': [
                            {'port': 80, 'protocol': 'tcp', 'status': 'open', 'service': 'http'},
                            {'port': 443, 'protocol': 'tcp', 'status': 'open', 'service': 'https'},
                        ]
                    },
                    {
                        'ip': '192.168.1.2',
                        'hostname': 'fileserver',
                        'status': 'up',
                        'ports': [
                            {'port': 21, 'protocol': 'tcp', 'status': 'open', 'service': 'ftp'},
                            {'port': 22, 'protocol': 'tcp', 'status': 'open', 'service': 'ssh'},
                        ]
                    }
                ],
                'latency': round(random.uniform(5, 100), 2),  # Random latency between 5-100ms
                'network_load': random.choice(['Low', 'Normal', 'High'])
            }

            maintenance_actions = ['Network Scan', 'Update Check', 'Configuration', 'System Restart', 'Security Audit']
            for i in range(5):  # Create 5 recent logs
                MaintenanceLog.objects.create(
                    probe=probe,
                    timestamp=timezone.now() - timezone.timedelta(minutes=i * 30),
                    # Recent activities in last few hours
                    action=random.choice(maintenance_actions),
                    details=f"Automated {maintenance_actions[i % len(maintenance_actions)].lower()} operation",
                    status=random.choice(['success', 'failed'])
                )

            probe_data = ProbeData.objects.create(
                probe=probe,
                data_type='network_scan',
                data=scan_data
            )
            self.stdout.write(f'Created network scan data for {probe.name}')

            # Create system status data
            system_data = {
                'cpu_percent': random.randint(10, 90),
                'memory_percent': random.randint(20, 80),
                'memory_used': random.randint(2, 8),
                'memory_total': 16,
                'disk_percent': random.randint(30, 95),
                'disk_used': random.randint(100, 900),
                'disk_total': 1000,
                'network_in': round(random.uniform(0.1, 10.0), 2),
                'network_out': round(random.uniform(0.1, 5.0), 2),
                'top_processes': [
                    {'pid': 1234, 'name': 'nginx', 'cpu_percent': 2.5, 'memory_percent': 1.2, 'status': 'running'},
                    {'pid': 2345, 'name': 'python', 'cpu_percent': 15.8, 'memory_percent': 5.6, 'status': 'running'},
                    {'pid': 3456, 'name': 'postgres', 'cpu_percent': 3.2, 'memory_percent': 8.7, 'status': 'running'}
                ]
            }

            probe_data = ProbeData.objects.create(
                probe=probe,
                data_type='system_status',
                data=system_data
            )
            self.stdout.write(f'Created system status data for {probe.name}')

        # Create maintenance logs
        for probe in probes:
            for i in range(3):
                status = random.choice(['success', 'failed'])
                action = random.choice(['update', 'restart', 'configuration', 'scan'])

                log = MaintenanceLog.objects.create(
                    probe=probe,
                    timestamp=timezone.now() - datetime.timedelta(days=i),
                    action=action,
                    details=f'{action.capitalize()} operation performed on {probe.name}',
                    status=status
                )
            self.stdout.write(f'Created maintenance logs for {probe.name}')

        # Create alerts
        severities = ['critical', 'warning', 'info']
        statuses = ['active', 'resolved']
        messages = [
            'Server unreachable',
            'High CPU usage detected',
            'Low disk space',
            'Network connectivity issues',
            'Memory usage exceeds threshold'
        ]

        for probe in probes:
            for i in range(random.randint(1, 5)):
                severity = random.choice(severities)
                status = random.choice(statuses)
                message = random.choice(messages)

                alert = Alert.objects.create(
                    probe=probe,
                    severity=severity,
                    status=status,
                    message=f'{message} on {probe.name}',
                    details=f'Alert details for {message.lower()} on {probe.hostname}.\nThis is a {severity} alert and requires attention.',
                    timestamp=timezone.now() - datetime.timedelta(hours=random.randint(1, 48)),
                    resolved_at=timezone.now() if status == 'resolved' else None
                )
            self.stdout.write(f'Created alerts for {probe.name}')

        self.stdout.write(self.style.SUCCESS('Successfully populated database with test data!'))