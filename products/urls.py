from django.urls import path

from products import views
from products.views import ProductDeleteView, CommentDeleteView, ProductUpdateView, CommentUpdateView

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product-list'),
    path('new/', views.AddProductView.as_view(), name='product-add'),
    path('details/<int:pk>', views.ProductDetailView.as_view(), name='product-details'),
    path('details/<str:slug>', views.ProductDetailView.as_view(), name='product-details'),
    path('delete/<int:pk>', ProductDeleteView.as_view(), name='product-delete'),
    path('delete/<str:slug>', ProductDeleteView.as_view(), name='product-delete'),
    path('edit/<int:pk>', ProductUpdateView.as_view(), name='product-edit'),
    path('edit/<str:slug>', ProductUpdateView.as_view(), name='product-edit'),
    path('comments/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
    path('comments/<int:pk>/edit/', CommentUpdateView.as_view(), name='comment-edit'),

]