from django.urls import path
from .views import InitiatePaymentView, HandleWebhookView 

urlpatterns = [
    path('v1/createpayment/',InitiatePaymentView.as_view(),name="create-payment"),
    path('v1/webhook/',HandleWebhookView.as_view(),name="webhook"),

]