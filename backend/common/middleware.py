import uuid

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

from common.logging import set_request_id


class RequestIDMiddleware:
    """Tags every request with an id so log lines can be correlated."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex)
        set_request_id(request.request_id)
        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        return response


class RateLimitMiddleware:
    """Small abuse guard for API endpoints; use gateway/Redis limits at scale."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith("/api/") or request.method == "OPTIONS":
            return self.get_response(request)
        identity = request.META.get("REMOTE_ADDR", "unknown")
        key = f"rate:{identity}:{request.path.rsplit('/', 2)[0]}"
        count = cache.get(key, 0) + 1
        cache.set(key, count, timeout=60)
        if count > settings.API_RATE_LIMIT_PER_MINUTE:
            return JsonResponse({"error": "Too many requests. Please retry shortly."}, status=429)
        return self.get_response(request)
