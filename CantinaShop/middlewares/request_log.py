import logging
import time

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('django.request')

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    This middleware logs information about each request.
    """

    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        duration = (time.time() - getattr(request, '_start_time', time.time())) * 1000

        user = getattr(request, 'user', None)
        username = user.username if user and user.is_authenticated else 'Anonymous'

        logger.info(
            f'{request.method} {request.get_full_path()} | '
            f'Status: {response.status_code} | '
            f'User: {username} | '
            f'Duration: {duration:.2f} ms'
        )

        return response