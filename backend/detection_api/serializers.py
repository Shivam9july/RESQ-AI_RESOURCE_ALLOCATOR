from rest_framework import serializers

from .models import Incident


class IncidentSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Incident
        fields = "__all__"
    
    def get_image_url(self, obj):
        if obj.image_file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.image_file.url)
            return obj.image_file.url
        return None
    
    def get_video_url(self, obj):
        if obj.video_file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.video_file.url)
            return obj.video_file.url
        return None


class FileUploadDetectionSerializer(serializers.Serializer):
    """Request payload for uploading and detecting disasters from images/videos."""
    
    image = serializers.FileField(required=False, help_text="Upload an image file")
    video = serializers.FileField(required=False, help_text="Upload a video file")
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    incident_type = serializers.ChoiceField(
        choices=["fire", "flood", "crowd"],
        required=False,
        help_text="Specify disaster type, or leave empty for auto-detection"
    )
    
    def validate(self, data):
        if not data.get("image") and not data.get("video"):
            raise serializers.ValidationError("Either image or video must be provided.")
        if data.get("image") and data.get("video"):
            raise serializers.ValidationError("Upload either an image or a video, not both.")
        return data


class VideoDetectionRequestSerializer(serializers.Serializer):
    """Request payload for running a detection model on a video (legacy)."""

    video_path = serializers.CharField(help_text="Path to the input video file.")
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)


class LoginSerializer(serializers.Serializer):
    """Request payload for dashboard operator login."""

    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False, write_only=True)

