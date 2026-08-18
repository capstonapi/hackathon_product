import uuid

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

from apps.articles.models import AuditEvent

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


class AuditMiddleware:
    """Record successful and failed state changes without storing user content."""

    MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/api/") and request.method in self.MUTATING_METHODS:
            try:
                actor = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
                AuditEvent.objects.create(
                    actor=actor,
                    event_type=f"api.{request.method.lower()}",
                    resource_type=request.path.strip("/").split("/")[1] if request.path.strip("/") else "",
                    request_id=getattr(request, "request_id", ""),
                    metadata={"path": request.path, "status_code": response.status_code},
                )
            except Exception:
                # Audit failures must be visible in server logs but must not
                # turn a user request into an outage.
                import logging
                logging.getLogger("news_agent.audit").exception("Failed to write audit event")
        return response
