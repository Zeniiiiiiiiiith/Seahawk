# Generated by Django 4.2.7 on 2024-12-12 13:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("harvester", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DiscoveredHost",
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
                ("mac_address", models.CharField(blank=True, max_length=17)),
                ("first_seen", models.DateTimeField(auto_now_add=True)),
                ("last_seen", models.DateTimeField(auto_now=True)),
                ("open_ports", models.JSONField(default=dict)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.RenameModel(
            old_name="NetworkScan",
            new_name="NetworkScanResult",
        ),
        migrations.RemoveField(
            model_name="harvesterconfig",
            name="config_data",
        ),
        migrations.RemoveField(
            model_name="harvesterconfig",
            name="is_active",
        ),
        migrations.RemoveField(
            model_name="harvesterconfig",
            name="last_update",
        ),
        migrations.AddField(
            model_name="harvesterconfig",
            name="gitlab_branch",
            field=models.CharField(default="main", max_length=50),
        ),
        migrations.AddField(
            model_name="harvesterconfig",
            name="gitlab_repo",
            field=models.URLField(
                default="https://gitlab.com/nfl-it/seahawks-monitoring.git",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="harvesterconfig",
            name="is_scanning",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="harvesterconfig",
            name="last_successful_scan",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="harvesterconfig",
            name="last_update_check",
            field=models.DateTimeField(null=True),
        ),
        migrations.DeleteModel(
            name="Host",
        ),
    ]
