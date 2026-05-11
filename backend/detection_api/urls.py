from django.urls import path

from . import views

urlpatterns = [
    path("auth/login/", views.LoginView.as_view(), name="auth-login"),
    path("auth/logout/", views.LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", views.CurrentOperatorView.as_view(), name="auth-me"),
    path("detect/fire/", views.FireDetectionView.as_view(), name="detect-fire"),
    path("detect/flood/", views.FloodDetectionView.as_view(), name="detect-flood"),
    path(
        "detect/social-distance/",
        views.SocialDistanceDetectionView.as_view(),
        name="detect-social-distance",
    ),
    path("detect/upload/", views.FileUploadDetectionView.as_view(), name="detect-upload"),
    path("incidents/", views.IncidentListView.as_view(), name="incident-list"),
]

