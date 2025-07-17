from django import forms
from django.template.defaultfilters import slugify

from common.image_cloud_storage import get_public_id_from_url, delete_cloudinary_image, upload_to_cloud_storage
from products.models import Product, Comment


class ProductForm(forms.ModelForm):
    image_file = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'block w-full text-sm text-gray-200 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-700 transition',
            'accept': 'image/*',
        })
    )


    def _generate_unique_slug(self, name):
        base_slug = slugify(name)
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def save(self, commit=True):
        product = super().save(commit=False)
        product.slug = self.cleaned_data.get('slug')

        image_file = self.cleaned_data.get('image_file')

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
            'name', 'description',  'price', 'is_available', 'image_file', 'quantity',
            'has_discount', 'tags', 'category',
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
                'class': 'h-5 w-5 text-indigo-600 bg-gray-700 border-gray-500 rounded focus:ring-indigo-500 transition',
            }),
            'has_discount': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-yellow-400 bg-gray-700 border-gray-500 rounded focus:ring-yellow-400 transition',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition',
            }),
            'tags': forms.TextInput(attrs={
                'placeholder': 'Comma-separated tags',
                'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        if name:
            slug = self._generate_unique_slug(name)
            cleaned_data['slug'] = slug

        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'rows': 4,
            'placeholder': 'Leave a comment...',
            'class': 'w-full px-4 py-3 rounded-lg bg-gray-700 border border-gray-600 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition'
        })
