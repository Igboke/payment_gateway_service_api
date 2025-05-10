from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from Products.models import Products
from clients.utils import Address

ClientModel = get_user_model()

STATUS_CHOICES=[
    ("pending",("Pending")),
    ("success",("Successful")),
    ("failed",("Failed"))
]
class Orders(models.Model):
    client = models.ForeignKey(ClientModel,on_delete=models.DO_NOTHING,related_name="orders",help_text="Select the Client making the Order")
    status = models.CharField(max_length=15,default="pending",choices=STATUS_CHOICES,help_text="Status Choices")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Order Total",null=False,blank=True)
    shipping_address = models.ForeignKey(Address,on_delete=models.SET_NULL,related_name="shipped_orders",help_text="Shipping Adress",null=True,blank=False)
    billing_address = models.ForeignKey(Address,on_delete=models.SET_NULL,help_text="Billing Adress",related_name="billed_orders",null=True,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]

    def calculate_total_amount(self):
        total = sum(item.product.price * item.quantity for item in self.order_line.all())
        self.total_amount = total
    
    def save(self, *args, **kwargs):
        if self.pk and not self.total_amount: 
            self.calculate_total_amount()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client} -- #Order No: {self.pk}"
    
class OrderItem(models.Model):
    products = models.ForeignKey(Products,on_delete=models.DO_NOTHING,related_name="product_items")
    orders = models.ForeignKey(Orders,on_delete=models.CASCADE,related_name="order_line")
    quantity = models.IntegerField(help_text="Enter OrderItem Quantity",validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.pk}"
    


