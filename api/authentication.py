from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import APIKey

class APIKeyAuthentication(BaseAuthentication):
    keyword = 'Api-Key'

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            keyword, key = auth_header.split(' ')
        except ValueError:
            raise AuthenticationFailed('Invalid Authorization header format.')

        if keyword != self.keyword:
            return None

        try:
            api_key = APIKey.objects.get(key=key, is_active=True)
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid or inactive API key.')

        if api_key.is_expired():
            raise AuthenticationFailed('API key expired.')

        user = api_key.user
        if not user.is_active:
            raise AuthenticationFailed('User inactive or deleted.')

        return (user, None)
