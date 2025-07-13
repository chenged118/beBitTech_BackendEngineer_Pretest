from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

def require_token(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        token = request.data.get('access_token') or request.query_params.get('access_token')
        if token != settings.ACCEPTED_TOKEN:
            return Response({"error": "Invalid access token."}, status=status.HTTP_403_FORBIDDEN)
        return view_func(request, *args, **kwargs)
    return wrapped_view