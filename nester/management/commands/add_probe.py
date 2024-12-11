from django.core.management.base import BaseCommand
from django.utils import timezone
from nester.models import Probe

class Command(BaseCommand):
    help = 'Add a new probe to the monitoring system'

    def add_arguments(self, parser):
        parser.add_argument('--name', required=True, help='Name of the probe')
        parser.add_argument('--hostname', required=True, help='Hostname of the probe')
        parser.add_argument('--ip', required=True, help='IP address of the probe')
        parser.add_argument('--status', default='offline', choices=['online', 'offline'], help='Status of the probe')
        parser.add_argument('--version', default='1.0', help='Version of the probe software')

    def handle(self, *args, **options):
        try:
            probe = Probe.objects.create(
                name=options['name'],
                hostname=options['hostname'],
                ip_address=options['ip'],
                status=options['status'],
                version=options['version'],
                last_contact=timezone.now() if options['status'] == 'online' else None
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created probe "{probe.name}"'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to create probe: {str(e)}'))