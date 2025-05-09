from django.db import models
from django.contrib.auth import get_user_model

ClientModel = get_user_model()

STATUS_CHOICES=[
    ("pending",("Pending")),
    ("success",("Successful")),
    ("failed",("Failed"))
]
class Orders(models.Model):
    client = models.ForeignKey(ClientModel,on_delete=models.CASCADE,related_name="orders",help_text="Select the Client making the Order")
    status = models.CharField(max_length=15,default="pending",choices=STATUS_CHOICES,help_text="Status Choices")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Order Total",null=True)
    shipping_address = models.CharField(max_length=100,help_text="Shipping Adress")
    billing_address = models.CharField(max_length=100,help_text="Billing Adress")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.client} -- #Order No: {Orders.pk}"
    


