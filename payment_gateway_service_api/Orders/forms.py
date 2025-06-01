from django import forms
from .models import Orders
import logging

logger = logging.getLogger(__name__)


class OrdersAdminForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = "__all__"

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status == "failed" and not self.instance.pk:
            logger.error("Attempt to mark a new order as failed.")
            raise forms.ValidationError(
                "An order cannot be marked as failed upon creation."
            )
        return status
