"""Middleware et filtres de logging (request id, sampling)."""

import uuid
import socket
import random
from threading import local as _thread_local
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

HOSTNAME = socket.gethostname()


class RequestIdMiddleware(MiddlewareMixin):
    """Génère/propague un X-Request-ID et X-Correlation-ID."""
    local = _thread_local()
    header_name = 'HTTP_X_REQUEST_ID'

    def process_request(self, request):  # type: ignore[override]
        rid = request.META.get(self.header_name) or str(uuid.uuid4())
        self.local.request_id = rid
        self.local.correlation_id = request.META.get('HTTP_X_CORRELATION_ID', rid)

    def process_response(self, request, response):  # type: ignore[override]
        rid = getattr(self.local, 'request_id', None)
        if rid:
            response['X-Request-ID'] = rid
        return response


class RequestIdFilter:
    """Ajoute request_id / correlation_id / host / environment aux records de log."""

    def filter(self, record):  # noqa: D401
        _local = RequestIdMiddleware.local
        record.request_id = getattr(_local, 'request_id', '-')
        record.correlation_id = getattr(_local, 'correlation_id', record.request_id)
        record.host = HOSTNAME
        record.environment = 'DEBUG' if settings.DEBUG else 'PROD'
        return True


class SamplingFilter:
    """Filtre les logs DEBUG selon LOG_SAMPLING_RATE (variable settings)."""

    def filter(self, record):  # noqa: D401
        rate = getattr(settings, 'LOG_SAMPLING_RATE', 1)
        if rate >= 1:
            return True
        if record.levelno <= 10:  # DEBUG
            return random.random() < rate
        return True
