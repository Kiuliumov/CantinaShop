from django.urls import path

from products import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product-list'),
    path('new/', views.AddProductView.as_view(), name='product-add'),
    path('details/<int:pk>', views.ProductDetailView.as_view(), name='product-details'),
]