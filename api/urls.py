from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from api.views import ProductListCreateAPIView, GenerateAPIKeyAPIView, ProductDetailAPIView

drf_spectacular = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
urlpatterns = [
    path('products/', ProductListCreateAPIView.as_view(), name='product-list-api-base'),
    path('products/<int:id>/', ProductDetailAPIView.as_view(), name='product-detail-api-base'),
    path('generate_key/', GenerateAPIKeyAPIView.as_view(), name='generate-key'),
] + drf_spectacular