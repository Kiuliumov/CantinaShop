from django.contrib.auth import authenticate
from django.core.files.uploadedfile import InMemoryUploadedFile

from common.image_cloud_storage import upload_to_cloud_storage, get_public_id_from_url, delete_cloudinary_image
from .models import UserModel, Account, Address
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms


class RegistrationForm(UserCreationForm):
    username = forms.CharField(label='Username', widget=forms.TextInput())
    email = forms.EmailField(required=True)
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'id': 'password'}),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        strip=False,
        widget=forms.PasswordInput(),
    )

    field_order = ['username', 'email', 'password1', 'password2']

    class Meta:
        model = UserModel
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        existing_users = UserModel.objects.filter(email=email)
        for user in existing_users:
            if not user.is_active:
                user.delete()
            else:
                raise forms.ValidationError("This email is already taken.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        existing_users = UserModel.objects.filter(username=username)
        for user in existing_users:
            if not user.is_active:
                user.delete()
            else:
                raise forms.ValidationError("This username is already taken.")
        return username

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username or Email")

    def clean(self):
        username_or_email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username_or_email and password:
            user = authenticate(self.request, username=username_or_email, password=password)
            if user is None:
                try:
                    user_obj = UserModel.objects.get(email=username_or_email)
                    user = authenticate(self.request, username=user_obj.username, password=password)
                except UserModel.DoesNotExist:
                    user = None

            if user is None:
                raise forms.ValidationError("Invalid username/email or password")
            else:
                self.confirm_login_allowed(user)

            self.user_cache = user

        return self.cleaned_data




class AccountForm(forms.ModelForm):

    """
    Shows account details and adds account data.
    """
    username = forms.CharField(max_length=150)
    profile_picture = forms.ImageField(required=False)
    street_address = forms.CharField(required=False)
    city = forms.CharField(required=False)
    state = forms.CharField(required=False)
    postal_code = forms.CharField(required=False)
    country = forms.CharField(required=False)

    class Meta:
        model = Account
        fields = [
            'username', 'phone_number', 'profile_picture',
            'street_address', 'city', 'state', 'postal_code', 'country',
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (
                existing_classes + ' w-full px-5 py-3 bg-gray-700 border border-gray-600 rounded-lg '
                'text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-3 focus:ring-indigo-500 '
                'focus:border-indigo-400 transition'
            ).strip()

        if user:
            self.fields['username'].initial = user.username

        if self.instance and hasattr(self.instance, 'default_shipping') and self.instance.default_shipping:
            addr = self.instance.default_shipping
            self.fields['street_address'].initial = addr.street_address
            self.fields['city'].initial = addr.city
            self.fields['state'].initial = addr.state
            self.fields['postal_code'].initial = addr.postal_code
            self.fields['country'].initial = addr.country

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = UserModel.objects.filter(username=username).exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if postal_code and len(postal_code) > 20:
            raise forms.ValidationError("Postal code cannot exceed 20 characters.")
        return postal_code

    def save(self, commit=True):
        account = super().save(commit=False)
        user = account.user

        new_username = self.cleaned_data['username']
        if user.username != new_username:
            user.username = new_username
            user.save()

        profile_picture: InMemoryUploadedFile = self.cleaned_data.get('profile_picture')

        if account.profile_picture_url:
            public_id = get_public_id_from_url(account.profile_picture_url)
            delete_cloudinary_image(public_id)

        if profile_picture:
            image_url = upload_to_cloud_storage(profile_picture)
            account.profile_picture_url = image_url

        if commit:
            account.save()

        address_data = {
            'street_address': self.cleaned_data.get('street_address', ''),
            'city': self.cleaned_data.get('city', ''),
            'state': self.cleaned_data.get('state', ''),
            'postal_code': self.cleaned_data.get('postal_code', ''),
            'country': self.cleaned_data.get('country', ''),
            'address_type': 'shipping',
            'account': account,
        }

        default_shipping = getattr(account, 'default_shipping', None)
        if default_shipping:
            for attr, value in address_data.items():
                setattr(default_shipping, attr, value)
            default_shipping.save()
        else:
            new_address = Address.objects.create(**address_data)
            account.default_shipping = new_address
            if commit:
                account.save()

        return account
