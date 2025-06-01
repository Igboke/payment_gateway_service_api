from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from django.conf import settings
import requests
import paystack
import logging

logger = logging.getLogger(__name__)


@dataclass
class PaymentDetails:
    """Data Transfer Object for payment details.
    This DTO encapsulates all necessary information to process a payment.
    - tx_ref: Unique reference for the transaction.
    - amount: Amount to be charged.
    - currency: Currency in which the payment is made.
    - client_email: Email of the client making the payment.
    - client_name: Name of the client making the payment.
    - is_permanent: Whether the payment is for a permanent service or not.
    - bank_code: Bank code for the payment.
    - bank_phone: Phone number associated with the bank account.
    - bank_token: Token for the bank account.
    """

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
    """Data Transfer Object for the response from a payment gateway after processing a payment.
    This DTO encapsulates the response data from the payment gateway after a payment attempt.
    - success: Indicates whether the payment was successful or not.
    - gateway_ref: Reference from the payment gateway for the transaction.
    - raw_response: Raw response data from the payment gateway. field(default_factory=dict) ensures that each instance gets its own independent dictionary.
    """

    success: bool
    gateway_ref: Optional[str] = None
    raw_response: Dict = field(default_factory=dict)


@dataclass
class GatewayWebhookEventDTO:
    """Data Transfer Object for webhook events from a payment gateway.
    This DTO encapsulates the data received from a payment gateway webhook event.
    - internal_transaction_ref: Internal reference for the transaction.
    - gateway_ref: Reference from the payment gateway for the transaction.
    - new_status: New status of the transaction as reported by the payment gateway.
    - amount: Amount associated with the transaction.
    """

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
    def process_payment(
        self, payment_details: PaymentDetails
    ) -> GatewayProcessPaymentResponseDTO:
        """Initiates a payment via this gateway. Returns core DTO based on gateway response."""
        pass

    @abstractmethod
    def handle_webhook(self, raw_webhook_data: Any) -> GatewayWebhookEventDTO:
        """Handles incoming raw webhook data, verifies, and returns core DTO."""
        pass

    @abstractmethod
    def verify_payment(self, transaction_ref: str) -> Dict[str, Any]:
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

    def process_payment(
        self, payment_details: PaymentDetails
    ) -> GatewayProcessPaymentResponseDTO:
        """
        Processes a payment using Paystack's API.
        This method takes payment details, constructs a request to Paystack's API,
        and returns a DTO with the result of the payment attempt.
        :param payment_details: PaymentDetails object containing all necessary information for the payment.
        :return: GatewayProcessPaymentResponseDTO containing the success status, gateway reference, and raw response data.
        """
        paystack.api_key = settings.PAYSTACK_SECRET_KEY
        amount = payment_details.amount * 100  # Paystack expects amount in kobo
        bank = {
            "code": payment_details.bank_code,
            "phone": payment_details.bank_phone,
            "token": payment_details.bank_token,
        }

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
            response_data = {
                "data": response.data,
                "message": response.message,
                "status": response.status,
            }
            logger.info(f"Processing payment: success={success}, data={response_data}")
        return GatewayProcessPaymentResponseDTO(
            success=success,
            gateway_ref=data.get("reference"),
            raw_response=response_data,
        )

    def handle_webhook(self, request_data) -> GatewayWebhookEventDTO:
        """
        Handles webhook notifications from Paystack
        This method processes the incoming webhook data, extracts relevant information,
        and returns a DTO with the transaction details.
        :param request_data: Raw data from the webhook notification.
        :return: GatewayWebhookEventDTO containing the internal transaction reference, gateway reference, new status, and amount.
        """

        data = request_data.get("data", {})
        transaction_ref = data.get("reference", "")
        status = data.get("status", "")
        gateway_ref = data.get("customer", "").get("customer_code", "")
        amount = data.get("amount", 0.0) // 100  # Convert to Naira
        logger.info(
            f"Handling webhook: tx_ref={transaction_ref}, status={status}, gateway_ref={gateway_ref}, amount={amount}"
        )
        return GatewayWebhookEventDTO(
            internal_transaction_ref=transaction_ref,
            gateway_ref=gateway_ref,
            new_status=status,
            amount=amount,
        )

    def verify_payment(self, transaction_ref: str):
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
        "Content-Type": "application/json",
    }

    def process_payment(
        self, payment_details: PaymentDetails
    ) -> GatewayProcessPaymentResponseDTO:
        """
        Processes a payment using FlutterWave's API.
        This method takes payment details, constructs a request to FlutterWave's API,
        and returns a DTO with the result of the payment attempt.
        :param payment_details: PaymentDetails object containing all necessary information for the payment.
        :return: GatewayProcessPaymentResponseDTO containing the success status, gateway reference, and raw response data.
        """
        endpoint = settings.FLUTTERWAVE_BANK_TRANSFER_ENDPOINT
        payload = {
            "amount": payment_details.amount,
            "email": payment_details.client_email,
            "currency": payment_details.currency,
            "tx_ref": payment_details.tx_ref,
            "full_name": payment_details.client_name,
            "is_permanent": payment_details.is_permanent,
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
            logger.info(
                f"Processing payment: success={success}, gateway_ref={gateway_ref}, data={data}"
            )

        return GatewayProcessPaymentResponseDTO(
            success=success, gateway_ref=gateway_ref, raw_response=data
        )

    def handle_webhook(self, request_data) -> GatewayWebhookEventDTO:
        """
        Handles webhook notifications from FlutterWave.
        This method processes the incoming webhook data, extracts relevant information,
        and returns a DTO with the transaction details.
        :param request_data: Raw data from the webhook notification.
        :return: GatewayWebhookEventDTO containing the internal transaction reference, gateway reference, new status, and amount.
        """

        data = request_data.get("data", {})
        transaction_ref = data.get("tx_ref", "")
        status = data.get("status", "")
        gateway_ref = data.get("flw_ref", "")
        amount = data.get("amount", 0.0)
        logger.info(
            f"Handling webhook: tx_ref={transaction_ref}, status={status}, gateway_ref={gateway_ref}, amount={amount}"
        )
        return GatewayWebhookEventDTO(
            internal_transaction_ref=transaction_ref,
            gateway_ref=gateway_ref,
            new_status=status,
            amount=amount,
        )

    def verify_payment(self, transaction_ref: str) -> dict:
        """
        Verifies a payment using FlutterWave's verification API.
        This method constructs a request to FlutterWave's verification endpoint
        and returns the verification result.
        :param transaction_ref: The transaction reference to verify.
        :return: A dictionary containing the verification result.
        """
        endpoint = settings.FLUTTERWAVE_VERIFICATION_URL.format(
            transaction_ref=transaction_ref
        )
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()
