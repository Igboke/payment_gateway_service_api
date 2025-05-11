from rest_framework import serializers
from Products.models import Products
from Orders.models import Orders, OrderItem
from django.contrib.auth import get_user_model

ClientModel = get_user_model()

class ClientModelSerializers(serializers.ModelSerializer):
    pass

class ProductsSerializers(serializers.ModelSerializer):
    pass

class OrdersSerializers(serializers.ModelSerializer):
    pass

class InitiatePaymentIncomingSerializers(serializers.Serializer):
    pass