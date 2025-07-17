from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages

from common.mixins import AdminRequiredMixin
from .forms import ProductForm
from products.models import Product, Category


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 9

    def get(self, request, *args, **kwargs):
        queryset = self.get_filtered_queryset()
        paginator = Paginator(queryset, 9)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        self.object_list = page_obj.object_list
        context = {
            'products': page_obj,
            'categories': Category.objects.all(),
            'querystring': self.get_querystring_without_page(request.GET)
        }
        return self.render_to_response(context)

    def get_filtered_queryset(self):
        qs = Product.objects.all()

        search_query = self.request.GET.get('search', '')
        if search_query:
            qs = qs.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

        category_id = self.request.GET.get('category')
        if category_id:
            qs = qs.filter(category_id=category_id)

        availability = self.request.GET.get('availability')
        if availability == 'available':
            qs = qs.filter(is_available=True)
        elif availability == 'unavailable':
            qs = qs.filter(is_available=False)

        sort_option = self.request.GET.get('sort')
        if sort_option == 'name_asc':
            qs = qs.order_by('name')
        elif sort_option == 'name_desc':
            qs = qs.order_by('-name')
        elif sort_option == 'price_asc':
            qs = qs.order_by('price')
        elif sort_option == 'price_desc':
            qs = qs.order_by('-price')

        return qs

    def get_querystring_without_page(self, get_params):
        params = get_params.copy()
        if 'page' in params:
            params.pop('page')
        return params.urlencode()



class AddProductView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/new_product.html'
    success_url = reverse_lazy('product-list')

    def form_valid(self, form):
        messages.success(self.request, "Product added successfully.")
        return super().form_valid(form)