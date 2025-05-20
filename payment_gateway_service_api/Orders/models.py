from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
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
    client = models.ForeignKey(ClientModel,on_delete=models.SET_NULL,related_name="orders",help_text="Select the Client making the Order",null=True,blank=False)
    status = models.CharField(max_length=15,default="pending",choices=STATUS_CHOICES,help_text="Status Choices")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Order Total",null=False,blank=True, default=0)
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

    def __str__(self):
        return f"{self.client} -- #Order No: {self.pk}"
    
class OrderItem(models.Model):
    product = models.ForeignKey(Products,on_delete=models.CASCADE,related_name="product_items")
    order = models.ForeignKey(Orders,on_delete=models.CASCADE,related_name="order_line")
    quantity = models.IntegerField(help_text="Enter OrderItem Quantity",validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.pk}"
    
class PaymentTransaction(models.Model):
    order = models.ForeignKey(Orders,on_delete=models.CASCADE,related_name="payment_transaction")#switch to protected
    client = models.ForeignKey(ClientModel,on_delete=models.CASCADE,related_name="client_payment")#switch to protected
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Payment Amount")
    status = models.CharField(max_length=15,default="pending",choices=STATUS_CHOICES,help_text="Payment Status")
    transaction_ref = models.CharField(max_length=255, unique=True, help_text="Internal transaction reference.")
    gateway_ref = models.CharField(max_length=255,null=True, unique=True, help_text="Payment gateway transaction reference.")
    gateway_name = models.CharField(max_length=50, help_text="Payment gateway name.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.gateway_name} - {self.transaction_ref} - {self.status}"


@receiver([post_delete,post_save], sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    """
    Update the total amount of the order when an OrderItem is saved or deleted.
    """
    order = instance.order
    order.calculate_total_amount()
    order.save(update_fields=["total_amount"])
