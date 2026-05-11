from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

def root_view(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><title>Resq API</title></head>
    <body style="font-family: system-ui; max-width: 600px; margin: 2rem auto; padding: 1rem;">
        <h1>Resq API</h1>
        <p>Backend is running. Use the dashboard or call the API:</p>
        <ul>
            <li><a href="/admin/">Admin</a></li>
            <li><a href="/api/incidents/">API: Incidents</a></li>
        </ul>
        <p><strong>Dashboard:</strong> Run the React app and open <a href="http://localhost:5173/">http://localhost:5173/</a></p>
    </body>
    </html>
    """
    return HttpResponse(html)

urlpatterns = [
    path("", root_view),
    path("admin/", admin.site.urls),
    path("api/", include("detection_api.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

