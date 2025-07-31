import json
import urllib.parse

from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy, reverse
from common.mixins import AdminRequiredMixin
from .forms import ProductForm, CommentForm, CategoryForm
from products.models import Product, Category, Comment, Rating
from django.contrib import messages


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

        category = self.request.GET.get('category')
        if category:
            if not category.isdigit():
                qs = qs.filter(category__name__exact=category)
            else:
                qs = qs.filter(category_id=category)

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


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_details.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = self.object.comments.select_related('account__user').order_by('-created_at')

        paginator = Paginator(comments, 5)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['comments'] = page_obj
        context['form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.product = self.object
            comment.account = request.user.account
            comment.save()
            messages.success(request, "Comment added successfully.")
            form = CommentForm()
        else:
            messages.error(request, "Failed to add comment.")
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class AddProductView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/new_product.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Product added successfully!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to add product. Please correct the errors below.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('product-details', kwargs={'slug': self.object.slug})


class ProductDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('product-list')

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect(self.success_url)

class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user
        if user != obj.account.user and not (user.is_staff or user.is_superuser):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        product_slug = obj.product.slug
        obj.delete()
        messages.success(request, "Comment deleted successfully.")
        return redirect('product-details', slug=product_slug)

    def get_success_url(self):
        comment = self.get_object()
        product_id = comment.product.id
        return self.request.META.get('HTTP_REFERER', reverse_lazy('product-details', kwargs={'pk': product_id}))


class ProductUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/edit_product.html'
    context_object_name = 'product'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Product updated successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update product.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('product-details', kwargs={'slug': self.object.slug})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user != obj.account.user and not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Comment updated successfully.")
        return response

    def form_invalid(self, form):
        product_slug = self.get_object().product.slug
        messages.error(self.request, "Failed to update comment!")
        return redirect('product-details', slug=product_slug)

    def get_success_url(self):
        return reverse_lazy('product-details', kwargs={'slug': self.object.product.slug})


class SetRatingView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        value = request.POST.get('rating')

        if not value:
            messages.error(request, "Rating value is missing.")
            return redirect('product-details', slug=product_slug)

        if not product_slug:
            raise Http404

        try:
            value = int(value)
            if not 1 <= value <= 5:
                raise ValueError
        except ValueError:
            messages.error(request, "Rating must be an integer between 1 and 5.")
            return redirect('product-details', slug=product_slug)

        product = get_object_or_404(Product, slug=product_slug)

        Rating.objects.update_or_create(
            user=request.user.account,
            product=product,
            defaults={'rating': value}
        )
        messages.success(request, "Your rating has been submitted.")
        return redirect(reverse_lazy('product-details', kwargs={'slug': product.slug}))


class CartView(View):
    def get(self, request):
        cart_cookie = request.COOKIES.get('cart')
        cart_data = []

        if cart_cookie:
            try:
                decoded_cookie = urllib.parse.unquote(cart_cookie)
                cart_data = json.loads(decoded_cookie)
            except (json.JSONDecodeError, TypeError):
                messages.error(request, "Failed to load your cart data. Starting with an empty cart!")
                cart_data = []

        items = []
        total = 0

        for entry in cart_data:
            slug = entry.get('slug')
            quantity = int(entry.get('quantity', 1))
            if not slug:
                continue

            product = Product.objects.filter(slug=slug).first()
            if product:
                subtotal = quantity * product.price
                total += subtotal
                items.append({
                    'product': product,
                    'quantity': quantity,
                    'subtotal': subtotal,
                })

        context = {
            'cart_items': items,
            'cart_total': total,
        }
        return render(request, 'shopping_cart/shopping_cart_list.html', context)


class CreateCategory(AdminRequiredMixin, CreateView):
    template_name = 'products/create_category.html'
    success_url = reverse_lazy('product-list')
    form_class = CategoryForm

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Category created successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to create category!")
        return super().form_invalid(form)