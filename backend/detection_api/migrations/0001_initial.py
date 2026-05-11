# Generated migration for detection_api.Incident

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name="Incident",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("incident_type", models.CharField(choices=[("fire", "Fire"), ("flood", "Flood"), ("crowd", "Crowd / Social Distance Violation")], max_length=16)),
                ("confidence", models.FloatField(help_text="Model confidence in the detection (0-1).")),
                ("latitude", models.FloatField(blank=True, null=True)),
                ("longitude", models.FloatField(blank=True, null=True)),
                ("detected_at", models.DateTimeField(auto_now_add=True)),
                ("meta", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "ordering": ["-detected_at"],
            },
        ),
    ]
