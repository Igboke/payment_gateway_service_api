from dataclasses import dataclass
import uuid
from django.conf import settings
from .payments_ports_and_adapters import (
    GatewayProcessPaymentResponseDTO,
    PaymentDetails,
    PaymentGatewayInterface,
)
from .repositories_ports_and_adapters import (
    ClientRepositoryInterface,
    CreateTransactionDTO,
    UpdateTransactionDTO,
)


@dataclass
class InitialPaymentRequestDTO:
    """
    Initial request data for payment initiation.
    Contains the necessary information to start a payment process.
    This DTO is used by the core service to initiate a payment.
    - client_email: The email of the client initiating the payment.
    - currency: The currency in which the payment is made.
    - payment_gateway_name: The name of the payment gateway to use.
    - is_permanent: Whether the payment is for a permanent service or not.
    - amount: The amount to be charged for the payment.
    """

    client_email: str
    currency: str
    payment_gateway_name: str
    is_permanent: bool = False
    amount: float = 0.0


@dataclass
class InitiatedPaymentResponseDTO:
    """
    Response DTO for initiated payment.
    Contains the transaction reference and the gateway response.
    This DTO is returned by the core service after initiating a payment.
    - transaction_ref: The reference for the initiated transaction.
    - gateway_response: The response from the payment gateway after processing the payment.
    """

    transaction_ref: str
    gateway_response: GatewayProcessPaymentResponseDTO


class PaymentServiceCore:
    """
    Core service for handling payment operations.
    This service is responsible for initiating payments and updating payment transactions
    based on webhook data from payment gateways.
    It uses the PaymentGatewayInterface to interact with different payment gateways
    and the ClientRepositoryInterface to manage client data and transactions.
    """

    def __init__(
        self,
        gateway_adapter: PaymentGatewayInterface,
        client_repository: ClientRepositoryInterface,
    ):
        self.gateway_adapter = gateway_adapter
        self.client_repository = client_repository

    def initiate_payment(
        self, request_data: InitialPaymentRequestDTO
    ) -> InitiatedPaymentResponseDTO:
        """
        Initiates a payment process for a client.
        """
        client = self.client_repository.get_client_by_email(request_data.client_email)

        if not client:
            settings.logger.error(
                f"Client with email {request_data.client_email} not found"
            )
            raise ValueError(f"Client with email {request_data.client_email} not found")

        latest_order_id, amount = (
            self.client_repository.get_latest_order_and_amount_for_client(client.id)
        )
        if not latest_order_id:
            settings.logger.error(f"No order found for client {client.id}")
            raise ValueError(f"No order found for client {client.id}")

        transaction_ref = str(uuid.uuid4())

        create_transaction_dto = CreateTransactionDTO(
            client_id=client.id,
            order_id=latest_order_id,
            amount=amount,
            transaction_ref=transaction_ref,
            gateway_name=request_data.payment_gateway_name,
        )

        initial_transaction = self.client_repository.create_payment_transaction(
            create_transaction_dto
        )

        payment_details_for_gateway = PaymentDetails(
            tx_ref=initial_transaction.transaction_ref,
            amount=initial_transaction.amount,
            currency=request_data.currency,
            client_email=client.email,
            client_name=client.full_name,
            is_permanent=request_data.is_permanent,
        )

        gateway_response_dto = self.gateway_adapter.process_payment(
            payment_details_for_gateway
        )

        update_transaction_dto = UpdateTransactionDTO(
            id=initial_transaction.id,
            gateway_ref=gateway_response_dto.gateway_ref,
            status="pending" if gateway_response_dto.success else "failed",
        )
        updated_transaction = self.client_repository.update_payment_transaction(
            initial_transaction.id, update_transaction_dto
        )

        return InitiatedPaymentResponseDTO(
            transaction_ref=updated_transaction.transaction_ref,
            gateway_response=gateway_response_dto,
        )

    def update_model_from_webhook(self, request_data):
        """
        Handles updating data using information gotten from the payment gateway webhook.
        This method processes the webhook data, retrieves the corresponding transaction,
        and updates the transaction status based on the webhook event.
        """
        # Call the core service method to handle the webhook
        gateway_webhook_data = self.gateway_adapter.handle_webhook(request_data)

        if not gateway_webhook_data.internal_transaction_ref:
            settings.logger.error("Transaction reference not found in the webhook data")
            raise ValueError("Transaction reference not found in the webhook data")
        transaction_model_id = self.client_repository.get_transaction_by_id(
            gateway_webhook_data.internal_transaction_ref
        )
        if not transaction_model_id:
            settings.logger.error(
                f"Transaction with reference {gateway_webhook_data.internal_transaction_ref} not found"
            )
            raise ValueError(
                f"Transaction with reference {gateway_webhook_data.internal_transaction_ref} not found"
            )

        update_transaction_dto = UpdateTransactionDTO(
            id=transaction_model_id,
            status=gateway_webhook_data.new_status,
            gateway_ref=gateway_webhook_data.gateway_ref,
            amount=gateway_webhook_data.amount,
        )

        payment_transaction_dto = self.client_repository.update_payment_transaction(
            transaction_model_id, update_transaction_dto
        )

        return payment_transaction_dto
