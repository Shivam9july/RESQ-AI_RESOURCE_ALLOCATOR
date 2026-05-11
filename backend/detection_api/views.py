from django.contrib.auth import authenticate, get_user_model, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .authentication import CsrfExemptSessionAuthentication
from .models import Incident
from .serializers import (
    LoginSerializer,
    IncidentSerializer, 
    VideoDetectionRequestSerializer,
    FileUploadDetectionSerializer
)
from .relief_calculator import (
    calculate_relief_amount,
)
from .prediction import predict_from_media, predict_from_video_path


def serialize_operator(user):
    display_name = user.get_full_name() or user.username or user.email
    role = "Administrator" if user.is_staff else "Operator"
    return {
        "id": user.id,
        "name": display_name,
        "email": user.email,
        "role": role,
        "is_staff": user.is_staff,
    }


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].strip().lower()
        password = serializer.validated_data["password"]
        User = get_user_model()

        try:
            username = User.objects.get(email__iexact=email).get_username()
        except User.DoesNotExist:
            username = email

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid email or password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            return Response(
                {"detail": "This account is inactive."},
                status=status.HTTP_403_FORBIDDEN,
            )

        login(request, user)
        return Response({"operator": serialize_operator(user)})


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentOperatorView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({"operator": serialize_operator(request.user)})


@method_decorator(csrf_exempt, name="dispatch")
class BaseDetectionView(APIView):
    """
    Base class for fire/flood/social-distance detection endpoints.

    In a real deployment this would call into the corresponding detector
    module in the top-level `detectors/` package.
    """

    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]
    incident_type: str = ""

    def post(self, request, *args, **kwargs):
        serializer = VideoDetectionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        video_path = data["video_path"]
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        prediction = predict_from_video_path(video_path, self.incident_type)
        relief_amount = calculate_relief_amount(
            prediction.incident_type,
            prediction.severity,
            prediction.affected_area,
            prediction.affected_population,
        )

        incident = Incident.objects.create(
            incident_type=prediction.incident_type,
            confidence=prediction.confidence,
            severity=prediction.severity,
            latitude=latitude,
            longitude=longitude,
            estimated_affected_area=prediction.affected_area,
            estimated_affected_population=prediction.affected_population,
            relief_amount=relief_amount,
            meta={**prediction.meta, "video_path": video_path},
        )

        serializer = IncidentSerializer(incident, context={'request': request})
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class FireDetectionView(BaseDetectionView):
    incident_type = "fire"


class FloodDetectionView(BaseDetectionView):
    incident_type = "flood"


class SocialDistanceDetectionView(BaseDetectionView):
    incident_type = "crowd"


@method_decorator(csrf_exempt, name="dispatch")
class FileUploadDetectionView(APIView):
    """
    Handle file uploads (images/videos) and detect disasters.
    Automatically calculates relief amounts based on detection results.
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = FileUploadDetectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        image_file = data.get("image")
        video_file = data.get("video")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        incident_type = data.get("incident_type")

        uploaded_file = image_file or video_file
        prediction = predict_from_media(
            filename=uploaded_file.name,
            size_bytes=uploaded_file.size,
            content_type=getattr(uploaded_file, "content_type", None),
            requested_type=incident_type,
        )
        relief_amount = calculate_relief_amount(
            prediction.incident_type,
            prediction.severity,
            prediction.affected_area,
            prediction.affected_population,
        )

        incident = Incident.objects.create(
            incident_type=prediction.incident_type,
            confidence=prediction.confidence,
            severity=prediction.severity,
            latitude=latitude,
            longitude=longitude,
            image_file=image_file,
            video_file=video_file,
            estimated_affected_area=prediction.affected_area,
            estimated_affected_population=prediction.affected_population,
            relief_amount=relief_amount,
            meta={
                **prediction.meta,
                "uploaded_file": uploaded_file.name,
                "file_size_mb": round(uploaded_file.size / (1024 * 1024), 2),
            },
        )

        serializer = IncidentSerializer(incident, context={'request': request})
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class IncidentListView(generics.ListAPIView):
    serializer_class = IncidentSerializer
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Incident.objects.only(
            "id",
            "incident_type",
            "confidence",
            "severity",
            "latitude",
            "longitude",
            "detected_at",
            "image_file",
            "video_file",
            "estimated_affected_area",
            "estimated_affected_population",
            "relief_amount",
            "meta",
        )
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
