from django.db import models

class Address(models.Model):
    """
    Address model for billing or shipping
    """
    street_line1 = models.CharField(max_length=255)
    street_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
