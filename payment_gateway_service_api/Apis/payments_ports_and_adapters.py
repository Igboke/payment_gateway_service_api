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
    def process_payment(self, payment_details: PaymentDetails) -> GatewayProcessPaymentResponseDTO:
        """Initiates a payment via this gateway. Returns core DTO based on gateway response."""
        pass

    @abstractmethod
    def handle_webhook(self, raw_webhook_data: Any) -> GatewayWebhookEventDTO:
        """Handles incoming raw webhook data, verifies, and returns core DTO."""
        pass

    @abstractmethod
    def verify_payment(self, transaction_ref: str) -> Dict[str, Any]: # Or return a GatewayVerificationResponseDTO?
        """Verifies a payment via this gateway. Returns gateway-specific response."""
        pass

class FlutterWaveAdapter(PaymentGatewayInterface):
    """
    Implements the PaymentGatewayInterface for the FlutterWave payment gateway.

    Unique behavior:
    - Processes payments by sending requests to FlutterWave's payment endpoint.
    - Handles webhook notifications specific to FlutterWave's format.
    - Verifies transactions using FlutterWave's verification API.
    """
    
    headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
    "Content-Type": "application/json"
    }
    
    def process_payment(self, payment_details: PaymentDetails) -> GatewayProcessPaymentResponseDTO:
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
        response.raise_for_status()
        data = response.json()

        # Translate FlutterWave response into core GatewayProcessPaymentResponseDTO
        success = data.get("status") == "success"
        gateway_ref = None
        if success and "meta" in data and "Authorization" in data["meta"]:
             gateway_ref = data["meta"]["Authorization"].get("transfer_reference")

        return GatewayProcessPaymentResponseDTO(
            success=success,
            gateway_ref=gateway_ref,
            raw_response=data
        )
    
    def handle_webhook(self, request) -> dict:
        # Handle webhook notifications from FlutterWave
        # This is a placeholder implementation
        return {"status": "Webhook received", "data": request.data}
    
    def verify_payment(self, transaction_ref: str) -> dict:
        # Verify payment using FlutterWave's verification API
        endpoint = f"https://api.flutterwave.com/v3/charges?tx_ref={transaction_ref}"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()

        
