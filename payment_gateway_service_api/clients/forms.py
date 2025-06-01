from django import forms
from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ValidationError
from .utils import Address

Client = get_user_model()


class AddressCreationForm(ModelForm):
    class Meta:
        model = Address
        fields = "__all__"


class ClientCreationForm(ModelForm):
    """
    This is the user creation Form
    """

    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password Confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = Client
        fields = "__all__"

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise ValidationError("Password do not Match")

        return password2

    def save(self, commit=True):
        """
        This is a Model Form, hence we have to override the save method to set password
        """
        # Create client instance but do not save
        client = super().save(commit=False)
        client.set_password(self.cleaned_data["password"])

        if commit:
            client.save()
            self.save_m2m()

        return client


class ClientChangeForm(UserChangeForm):
    """
    Client Change form inherits from User Change Form
    """

    class Meta:
        model = Client
        fields = "__all__"
