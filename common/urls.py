from django.urls import path

from common import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('about/', views.About.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
]