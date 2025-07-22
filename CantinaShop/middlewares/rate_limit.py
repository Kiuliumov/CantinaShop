import time
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limit middleware using Django cache.
    Limits requests per IP address.

    RATE_LIMIT = {
        'RATE': 50,        # Number of requests
        'PERIOD': 60,      # Time window in seconds
        'CACHE_KEY_PREFIX': 'rl:',
    }
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        config = getattr(settings, "RATE_LIMIT", {})
        self.rate = config.get("RATE", 50)
        self.period = config.get("PERIOD", 60)
        self.cache_key_prefix = config.get("CACHE_KEY_PREFIX", "rl:")

    def process_request(self, request):
        ip = self.get_client_ip(request)
        if ip:
            cache_key = f"{self.cache_key_prefix}{ip}"
            now = time.time()
            request_times = cache.get(cache_key, [])

            request_times = [t for t in request_times if t > now - self.period]

            if len(request_times) >= self.rate:
                retry_after = int(request_times[0] + self.period - now)

                return render(
                    request,
                    "middleware_pages/too_many_requests.html",
                    status=429,
                    context={"retry_after_seconds": retry_after}
                )

            request_times.append(now)
            cache.set(cache_key, request_times, timeout=self.period)

    def get_client_ip(self, request):
        """Get client IP address considering proxies."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
