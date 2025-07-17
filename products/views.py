from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from .forms import ProductForm
from products.models import Product


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        qs = super().get_queryset()
        paginator = Paginator(qs, 9)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return page_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.get_queryset()
        return context

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied

class AddProductView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/new_product.html'
    success_url = reverse_lazy('product-list')

    def form_valid(self, form):
        messages.success(self.request, "Product added successfully.")
        return super().form_valid(form)