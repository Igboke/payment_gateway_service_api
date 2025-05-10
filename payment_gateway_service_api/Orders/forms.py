from django import forms
from .models import Orders

class OrdersAdminForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = '__all__'

    def clean_status(self):
        status = self.cleaned_data['status']
        if status == 'failed' and not self.instance.pk:
            raise forms.ValidationError("An order cannot be marked as failed upon creation.")
        return status