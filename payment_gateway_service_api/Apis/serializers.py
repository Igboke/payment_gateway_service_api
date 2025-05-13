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

class ProductsSerializers(serializers.ModelSerializer):
    """
    Product Serializer
    """
    class Meta:
        model = Products
        fields = [
            "id",
            "name",
            "quantity"
            "description",
            "price",
            "is_available",
        ]

class OrdersSerializers(serializers.ModelSerializer):
    """
    Order Serializer
    """
    client = ClientModelSerializers(read_only=True)
    shipping_address = AddressSerializers(many=True)
    billing_address = AddressSerializers(many=True)
    order_line = serializers.PrimaryKeyRelatedField(many=True, queryset=OrderItem.objects.all())

    class Meta:
        model = Orders
        fields = [
            "id",
            "client",
            "status",
            "total_amount",
            "shipping_address",
            "billing_address",
            "order_line",
        ]

class BankTransferSerializers(serializers.Serializer):
    """
    Serializer for incoming Bank payment request
    """
    # amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    email = serializers.EmailField()
    currency = serializers.CharField(max_length=3,default="NGN")
    # tx_ref = serializers.CharField(max_length=100)
    # fullname = serializers.CharField(max_length=100)
    is_permanent = serializers.BooleanField(default=False)

class BankTransferOutputSerializers(serializers.Serializer):
    """
    Serializer for output Bank payment response
    """
    transaction_ref = serializers.CharField(max_length=100)
    gateway_response =serializers.JSONField()
