"""Structured logging: one JSON object per line, tagged with a request id."""
import contextvars
import json
import logging

_request_id_var = contextvars.ContextVar("request_id", default=None)


def set_request_id(request_id):
    _request_id_var.set(request_id)


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = _request_id_var.get()
        return True


class JSONFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload)
