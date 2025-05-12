from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from .utils import ClientPaymentDetails
from .core_logic import PaymentDetails
from django.conf import settings
import requests

@dataclass
class PaymentDetails:
    tx_ref: str
    amount: float
    currency: str
    client_email: str
    client_name: str
    is_permanent: bool = False

@dataclass
class GatewayProcessPaymentResponseDTO:
    success: bool
    gateway_ref: Optional[str] = None
    redirect_url: Optional[str] = None
    raw_response: Dict = field(default_factory=dict)

@dataclass
class GatewayWebhookEventDTO:
     gateway_ref: str
     event_type: str
     new_status: str 
     amount: float

class PaymentGatewayInterface(ABC):
    """Interface for payment gateway adapters.
    Methods in this interface should be implemented by all payment gateway adapters.
    Each adapter should handle its own specific logic for:
    - processing payments,
    - handling webhooks, 
    - verifying payments.
    """
    @abstractmethod
    def process_payment(self, payment_details: PaymentDetails,client_payment_details_instance:ClientPaymentDetails) -> dict:
        """Initiates a payment via this gateway. Returns gateway-specific response."""
        pass

    @abstractmethod
    def handle_webhook(self, request: Any) -> dict:
        """Handles incoming webhook notifications from the payment gateway. Returns processed data."""
        pass

    @abstractmethod
    def verify_payment(self, transaction_ref: str) -> dict:
        """Verifies a payment via this gateway. Returns gateway-specific response."""
        pass

class FlutterWaveAdapter(PaymentGatewayInterface):
    """
    Implements the PaymentGatewayInterface for the FlutterWave payment gateway.

    def process_payment(self, payment_details: PaymentDetails):
    providing methods to process payments, handle webhook notifications, and 
    verify transactions. It ensures that all interactions with FlutterWave 
    adhere to the gateway's API specifications.

    Unique behavior:
    - Processes payments by sending requests to FlutterWave's payment endpoint.
    - Handles webhook notifications specific to FlutterWave's format.
    - Verifies transactions using FlutterWave's verification API.

    Note: This is a placeholder implementation and should be extended with 
    actual API calls to FlutterWave's services.
    """
    
    headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
    "Content-Type": "application/json"
    }
    
    def process_payment(self, payment_details,client_payment_details_instance) -> dict:
        # Process payment using FlutterWave's bank transfer endpoint
        endpoint = settings.FLUTTERWAVE_BANK_TRANSFER_ENDPOINT
        payload = {
            "amount": payment_details.amount,   
            "email": payment_details.client_email,
            "currency": payment_details.currency,
            "tx_ref": payment_details.tx_ref,
            "full_name": payment_details.client_name,
            "is_permanent": payment_details.is_permanent
        }
        response = requests.post(endpoint, json=payload, headers=self.headers)
        data = response.json()
        return data
           
    def update_payment_details(self,data:Dict[str, Any],payment_details,client_payment_details_instance) -> dict:
        # Update payment details in the database
        if data["status"] == "success":
            # Update the transaction model with the response data
            client_payment_details_instance.gateway_ref = data["meta"]["Authorization"]["transfer_reference"]
            client_payment_details_instance.amount = payment_details.amount
            client_payment_details_instance.payment_status = "pending"
            client_payment_details_instance.save()
            
    
    def handle_webhook(self, request) -> dict:
        # Handle webhook notifications from FlutterWave
        # This is a placeholder implementation
        return {"status": "Webhook received", "data": request.data}
    
    def verify_payment(self, transaction_ref: str) -> dict:
        # Verify payment using FlutterWave's verification API
        endpoint = f"https://api.flutterwave.com/v3/charges?tx_ref={transaction_ref}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json()

        
