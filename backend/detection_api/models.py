from django.db import models


class Incident(models.Model):
    """Stores a detected disaster incident (fire, flood, crowding, etc.)."""

    INCIDENT_TYPES = [
        ("fire", "Fire"),
        ("flood", "Flood"),
        ("crowd", "Crowd / Social Distance Violation"),
    ]

    SEVERITY_LEVELS = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    incident_type = models.CharField(max_length=16, choices=INCIDENT_TYPES)
    confidence = models.FloatField(help_text="Model confidence in the detection (0-1).")
    severity = models.CharField(
        max_length=16, 
        choices=SEVERITY_LEVELS, 
        default="medium",
        help_text="Severity level of the disaster"
    )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    detected_at = models.DateTimeField(auto_now_add=True)
    
    # File uploads
    image_file = models.FileField(upload_to="incidents/images/", null=True, blank=True)
    video_file = models.FileField(upload_to="incidents/videos/", null=True, blank=True)
    
    # Relief calculation
    estimated_affected_area = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Estimated affected area in square kilometers"
    )
    estimated_affected_population = models.IntegerField(
        null=True, 
        blank=True, 
        help_text="Estimated number of affected people"
    )
    relief_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Calculated relief amount in USD"
    )
    
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-detected_at"]
        indexes = [
            models.Index(fields=["-detected_at"], name="incident_detected_desc_idx"),
            models.Index(fields=["incident_type"], name="incident_type_idx"),
            models.Index(fields=["severity"], name="incident_severity_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.get_incident_type_display()} @ {self.detected_at:%Y-%m-%d %H:%M:%S}"

