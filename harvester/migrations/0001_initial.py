# Generated by Django 4.2.7 on 2024-12-11 12:38

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="HarvesterConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("hostname", models.CharField(max_length=255)),
                ("local_ip", models.GenericIPAddressField()),
                ("version", models.CharField(max_length=50)),
                ("last_update", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("scan_interval", models.IntegerField(default=3600)),
                ("config_data", models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name="NetworkScan",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                ("network_address", models.CharField(max_length=50)),
                ("total_hosts", models.IntegerField()),
                ("scan_data", models.JSONField()),
                ("latency", models.FloatField(null=True)),
            ],
            options={
                "ordering": ["-timestamp"],
            },
        ),
        migrations.CreateModel(
            name="Host",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ip_address", models.GenericIPAddressField()),
                ("hostname", models.CharField(blank=True, max_length=255)),
                ("status", models.CharField(max_length=50)),
                ("last_seen", models.DateTimeField(auto_now=True)),
                ("ports", models.JSONField(default=dict)),
                (
                    "scan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hosts",
                        to="harvester.networkscan",
                    ),
                ),
            ],
        ),
    ]