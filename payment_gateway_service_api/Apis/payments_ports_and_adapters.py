from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from django.conf import settings
import requests
import paystack

@dataclass
class PaymentDetails:
    tx_ref: str
    amount: float
    currency: str
    client_email: str
    client_name: str
    is_permanent: bool = False
    bank_code: str = "50211"
    bank_phone: str = "+2348100000000"
    bank_token: str = "123456"


@dataclass
class GatewayProcessPaymentResponseDTO:
    success: bool
    gateway_ref: Optional[str] = None
    raw_response: Dict = field(default_factory=dict)

@dataclass
class GatewayWebhookEventDTO:
    internal_transaction_ref: str
    gateway_ref: str
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

class PayStackAdapter(PaymentGatewayInterface):
    """
    Implements the PaymentGatewayinterface for the FLuterWave payment gateway

    Unique behaviour:
    - Processes payment by sending requests to paystack's payment endpoint
    - Handles webhook notifications specific to flutterwave's format.
    - Verifies transaction using Paystack's verification API
    """
    def process_payment(self, payment_details:PaymentDetails) -> GatewayProcessPaymentResponseDTO:
        # Initialize Paystack client
        paystack.api_key = settings.PAYSTACK_SECRET_KEY
        amount = payment_details.amount * 100  # Paystack expects amount in kobo
        bank = {
            "code": payment_details.bank_code,#"50211",
            "phone": payment_details.bank_phone,#"+2348100000000",
            "token": payment_details.bank_token,#"123456"
        }
 

        # Create a payment charge request
        response = paystack.Charge.create(
            email=payment_details.client_email,
            amount=amount,
            bank=bank,
            reference=payment_details.tx_ref,
            
        )
        if response:
            status = response.status
            data = response.data
            success = status == True
            response_data = {"data":response.data,
                    "message":response.message,
                    "status":response.status
            }
        return GatewayProcessPaymentResponseDTO(
            success=success,
            gateway_ref=data.get("reference"),
            raw_response=response_data
        )

    def handle_webhook(self, request_data) -> GatewayWebhookEventDTO:
        """
        Handles webhook notifications from Paystack
        """
        # Handle webhook notifications from Paystack
        # simply for extracting data and passing to a dto (GatewayWebhookEventDTO)
        data = request_data.get("data", {})
        transaction_ref = data.get("reference", "")
        status = data.get("status", "")
        gateway_ref = data.get("customer", "").get("customer_code", "")
        amount = data.get("amount", 0.0)//100  # Convert to Naira
        return GatewayWebhookEventDTO(
            internal_transaction_ref=transaction_ref,
            gateway_ref=gateway_ref,
            new_status=status,
            amount=amount
        )

    def verify_payment(self, transaction_ref:str):
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
        success = data.get("status") == "success"
        gateway_ref = None
        if success:
            meta = data.get("meta", {})
            authorization = meta.get("Authorization", {})
            gateway_ref = authorization.get("transfer_reference")

        return GatewayProcessPaymentResponseDTO(
            success=success,
            gateway_ref=gateway_ref,
            raw_response=data
        )
    
    def handle_webhook(self, request_data) -> GatewayWebhookEventDTO:
        # Handle webhook notifications from FlutterWave
        # simply for extracting data and passing to a dto
        data = request_data.get("data", {})
        transaction_ref = data.get("tx_ref", "")
        status = data.get("status", "")
        gateway_ref = data.get("flw_ref", "")
        amount = data.get("amount", 0.0)
        return GatewayWebhookEventDTO(
            internal_transaction_ref=transaction_ref,
            gateway_ref=gateway_ref,
            new_status=status,
            amount=amount
        )
    
    def verify_payment(self, transaction_ref: str) -> dict:
        # Verify payment using FlutterWave's verification API
        endpoint = f"https://api.flutterwave.com/v3/charges?tx_ref={transaction_ref}"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()

        
