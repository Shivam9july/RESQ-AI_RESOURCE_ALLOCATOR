from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Session auth for the local API consumed by the React dashboard."""

    def enforce_csrf(self, request):
        return None
