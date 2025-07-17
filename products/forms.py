from django import forms
from django.template.defaultfilters import slugify

from common.image_cloud_storage import get_public_id_from_url, delete_cloudinary_image, upload_to_cloud_storage
from products.models import Product


class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].widget = forms.HiddenInput()

    def save(self, commit=True):
        product = super().save(commit=False)

        if not product.slug and product.name:
            product.slug = slugify(product.name)

        image_file = self.cleaned_data.get('image')

        if product.image_url:
            public_id = get_public_id_from_url(product.image_url)
            delete_cloudinary_image(public_id)

        if image_file:
            product.image_url = upload_to_cloud_storage(image_file)

        if commit:
            product.save()

        return product

    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'is_available', 'image_url', 'quantity',
            'slug', 'has_discount', 'tags', 'category',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition',
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition',
                'step': '0.01',
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'rounded text-indigo-500 focus:ring-indigo-500 focus:ring-2 focus:ring-offset-0',
            }),
            'image_url': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-200 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-700 transition',
                'accept': 'image/*',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition',
            }),
            'slug': forms.HiddenInput(),
            'has_discount': forms.CheckboxInput(attrs={
                'class': 'rounded text-yellow-400 focus:ring-yellow-400 focus:ring-2 focus:ring-offset-0',
            }),
            'tags': forms.TextInput(attrs={
                'placeholder': 'Comma-separated tags',
                'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition',
            }),
        }
