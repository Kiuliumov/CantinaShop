from django.urls import path

from products import views
from products.views import ProductDeleteView, CommentDeleteView, ProductUpdateView, CommentUpdateView

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product-list'),
    path('new/', views.AddProductView.as_view(), name='product-add'),
    path('details/<slug:slug>/', views.ProductDetailView.as_view(), name='product-details'),
    path('delete/<slug:slug>/', views.ProductDeleteView.as_view(), name='product-delete'),
    path('edit/<slug:slug>/', views.ProductUpdateView.as_view(), name='product-edit'),
    path('comments/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment-delete'),
    path('comments/<int:pk>/edit/', views.CommentUpdateView.as_view(), name='comment-edit'),
    path('rate/<slug:slug>', views.SetRatingView.as_view(), name='rate'),
    path('cart/', views.CartView.as_view(), name='cart'),
]