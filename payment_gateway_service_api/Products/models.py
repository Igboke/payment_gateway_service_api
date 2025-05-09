from django.db import models
from django.db.models import Q, CheckConstraint
from django.core.validators import MinValueValidator

class Products(models.Model):
    """
    This is the model for the products
    """
    name = models.CharField(max_length=255, unique=True, help_text="Enter Product Name")
    quantity = models.IntegerField(help_text="Enter Product Quantity",validators=[MinValueValidator(0)])
    description = models.TextField(help_text="Enter Product Description")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Enter Product Price")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Enter Date Created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Enter Date Updated")
    is_available = models.BooleanField(default=True, help_text="Is Product Available")

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_at"]
        constraints = [
            CheckConstraint(
                check=Q(quantity__gte=0),
                name="quantity_greater_than_zero",
            ),
        ]
