from django.contrib.auth import authenticate

from .models import UserModel
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
                raise forms.ValidationError("This email is already registered and active.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        existing_users = UserModel.objects.filter(username=username)
        for user in existing_users:
            if not user.is_active:
                user.delete()
            else:
                raise forms.ValidationError("This username is already taken by an active user.")
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