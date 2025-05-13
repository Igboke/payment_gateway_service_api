from django.urls import path
from .views import InitiatePaymentView 

urlpatterns = [
    path('v1/createpayment/',InitiatePaymentView.as_view(),name="create-payment")
]