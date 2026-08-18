"""
Single DRF exception boundary: every error response is `{"error": "..."}"`.

Never lets a raw traceback, prompt text, or API key reach the client -- an
unhandled exception is logged server-side (with the request id for
correlation) and turned into a generic 500 message.
"""
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("news_agent.api")

_GENERIC_MESSAGE = "An unexpected error occurred while processing this request."


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        detail = response.data.get("detail") if isinstance(response.data, dict) else response.data
        response.data = {"error": detail if isinstance(detail, str) else "Request could not be processed."}
        return response

    logger.error("Unhandled exception in %s", context.get("view"), exc_info=exc)
    return Response({"error": _GENERIC_MESSAGE}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
