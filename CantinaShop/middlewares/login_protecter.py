import time
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin


class LoginDefenderMiddleware(MiddlewareMixin):
    """
    Middleware to throttle failed login attempts by IP address.
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        config = getattr(settings, "LOGIN_DEFENDER", {})
        self.max_attempts = config.get("MAX_ATTEMPTS", 5)
        self.block_duration = config.get("BLOCK_DURATION", 300)
        self.cache_prefix = config.get("CACHE_KEY_PREFIX", "login_defend:")

    def process_request(self, request):
        if request.path == settings.LOGIN_URL and request.method == "POST":
            ip = self.get_client_ip(request)
            cache_key = f"{self.cache_prefix}{ip}"
            data = cache.get(cache_key, {"failures": 0, "timestamp": 0})

            now = time.time()
            if data["failures"] >= self.max_attempts:
                retry_after = int(data["timestamp"] + self.block_duration - now)
                if retry_after > 0:
                    return render(
                        request,
                        "middleware_pages/login_attempts.html",
                        context={"retry_after_seconds": retry_after},
                        status=429,
                    )
                else:
                    data = {"failures": 0, "timestamp": now}
                    cache.set(cache_key, data, timeout=self.block_duration)

    def process_response(self, request, response):
        if request.path == settings.LOGIN_URL and request.method == "POST":
            if request.user.is_anonymous and response.status_code in (200, 401):
                ip = self.get_client_ip(request)
                cache_key = f"{self.cache_prefix}{ip}"
                data = cache.get(cache_key, {"failures": 0, "timestamp": 0})

                data["failures"] += 1
                data["timestamp"] = time.time()

                cache.set(cache_key, data, timeout=self.block_duration)

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
