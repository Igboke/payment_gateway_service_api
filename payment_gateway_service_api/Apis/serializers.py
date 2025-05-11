from rest_framework import serializers
from Products.models import Products
from Orders.models import Orders, OrderItem
from django.contrib.auth import get_user_model
from clients.utils import Address

ClientModel = get_user_model()

class AddressSerializers(serializers.ModelSerializer):
    """
    Address Serializer
    """
    class Meta:
        model = Address
        fields = [
            "id",
            "street_line_1",
            "street_line_2",
            "city",
            "state_province",
            "postal_code",
            "country",
        ]

class ClientModelSerializers(serializers.ModelSerializer):
    """
    Client Serializer
    """
    house_address = AddressSerializers(many=True, required=False)
    class Meta:
        model = ClientModel
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "house_address",
        ]
    pass

class ProductsSerializers(serializers.ModelSerializer):
    pass

class OrdersSerializers(serializers.ModelSerializer):
    pass

class InitiatePaymentIncomingSerializers(serializers.Serializer):
    pass