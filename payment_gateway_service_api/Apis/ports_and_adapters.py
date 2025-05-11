from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from .core_logic import PaymentDetails

class PaymentGatewayInterface(ABC):
    """Interface for payment gateway adapters.
    Methods in this interface should be implemented by all payment gateway adapters.
    Each adapter should handle its own specific logic for processing payments,
    handling webhooks, and verifying payments.
    """
    @abstractmethod
    def process_payment(self, payment_details: PaymentDetails) -> dict:
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
