from abc import ABC, abstractmethod
from typing import Optional, Any
from dataclasses import dataclass
from django.contrib.auth import get_user_model
from Orders.models import PaymentTransaction, Orders
import logging

logger = logging.getLogger(__name__)


@dataclass
class ClientDTO:
    """Data Transfer Object for client details.
    This DTO is used to transfer client information between layers of the application.
    Attributes:
        id: Unique identifier for the client.
        email: Email address of the client.
        full_name: Full name of the client.
    """

    id: Any
    email: str
    full_name: str


@dataclass
class PaymentTransactionDTO:
    """Data Transfer Object for payment transaction details.
    This DTO is used to transfer payment transaction information between layers of the application.
    Attributes:
        id: Unique identifier for the payment transaction.
        transaction_ref: Reference for the transaction.
        amount: Amount involved in the transaction.
        client_id: Unique identifier for the client associated with the transaction.
        order_id: Unique identifier for the order associated with the transaction.
        status: Current status of the transaction (e.g., pending, completed, failed).
        gateway_name: Name of the payment gateway used for the transaction.
        gateway_ref: Reference from the payment gateway for the transaction.
    """

    id: Any
    transaction_ref: str
    amount: float
    client_id: Any
    order_id: Any
    status: str
    gateway_name: Optional[str] = None
    gateway_ref: Optional[str] = None


@dataclass
class CreateTransactionDTO:
    """Data Transfer Object for creating a payment transaction.
    This DTO is used to encapsulate the data required to create a new payment transaction.
    Attributes:
        client_id: Unique identifier for the client initiating the transaction.
        order_id: Unique identifier for the order associated with the transaction.
        amount: Amount to be processed in the transaction.
        transaction_ref: Reference for the transaction.
        gateway_name: Optional name of the payment gateway to be used for the transaction.
    """

    client_id: Any
    order_id: Any
    amount: float
    transaction_ref: str
    gateway_name: Optional[str] = None


@dataclass
class UpdateTransactionDTO:
    """Data Transfer Object for updating a payment transaction.
    This DTO is used to encapsulate the data required to update an existing payment transaction.
    Attributes:
        id: Unique identifier for the payment transaction to be updated.
        status: Optional new status for the transaction (e.g., pending, completed, failed).
        gateway_ref: Optional reference from the payment gateway for the transaction.
        amount: Optional new amount for the transaction.
    """

    id: Any
    status: Optional[str] = None
    gateway_ref: Optional[str] = None
    amount: Optional[float] = None


class ClientRepositoryInterface(ABC):
    """Port for accessing client and payment transaction data."""

    @abstractmethod
    def get_client_by_email(self, email: str) -> Optional[ClientDTO]:
        """Retrieve client details by email."""
        pass

    @abstractmethod
    def get_transaction_by_id(self, transaction_ref: Any) -> int:
        """Retrieve a payment transaction by its Internal Transaction ID- UUID."""
        pass

    @abstractmethod
    def create_payment_transaction(
        self, transaction_data: CreateTransactionDTO
    ) -> PaymentTransactionDTO:
        """Create a new payment transaction record."""
        pass

    @abstractmethod
    def update_payment_transaction(
        self, transaction_id: Any, update_data: UpdateTransactionDTO
    ) -> PaymentTransactionDTO:
        """Update an existing payment transaction record."""
        pass

    @abstractmethod
    def get_latest_order_and_amount_for_client(
        self, client_id: Any
    ) -> list[int | None]:
        """Get the ID/details and amount of the client's latest order."""
        pass


ClientModel = get_user_model()


class DjangoClientRepositoryAdapter(ClientRepositoryInterface):
    """Django ORM adapter for the ClientRepositoryInterface.
    This adapter implements the methods defined in the ClientRepositoryInterface using Django's ORM to interact with the database.
    It provides methods to retrieve client details, create and update payment transactions,
    and retrieve the latest order for a client.
    """

    def get_client_by_email(self, email: str) -> Optional[ClientDTO]:
        """Retrieve client details by email.
        Args:
            email (str): The email address of the client to retrieve.
        Returns:
            Optional[ClientDTO]: A ClientDTO object containing the client's details if found, otherwise None.
        """
        try:
            client_model = ClientModel.objects.get(email=email)
            logger.info(f"Client found: {client_model.email}")
            return ClientDTO(
                id=client_model.pk,
                email=client_model.email,
                full_name=client_model.get_full_name(),
            )
        except ClientModel.DoesNotExist:
            logger.error(f"Client with email {email} does not exist.")
            return None

    def get_transaction_by_id(self, transaction_ref):
        """Retrieve a payment transaction by its Internal Transaction ID- UUID.
        Args:
            transaction_ref (Any): The transaction reference to retrieve.
        Returns:
            int: The primary key of the payment transaction if found.
        Raises:
            ValueError: If the transaction reference is not found in the webhook data.
        """
        transaction_model = PaymentTransaction.objects.get(
            transaction_ref=transaction_ref
        )
        if not transaction_model:
            logger.error(
                f"Transaction reference {transaction_ref} not found in the webhook data."
            )
            raise ValueError("Transaction reference not found in the webhook data")
        logger.info(f"Transaction found: {transaction_model.transaction_ref}")
        return transaction_model.pk

    def get_latest_order_and_amount_for_client(
        self, client_id: Any
    ) -> list[int | None]:
        """Get the ID/details and amount of the client's latest order.
        Args:
            client_id (Any): The unique identifier of the client.
        Returns:
            list (int | None): A list containing the latest order ID and the total amount of that order.
                              If no order exists, returns [None, None].
        """
        try:
            order = Orders.objects.filter(client_id=client_id).latest("created_at")
            amount = (
                float(order.total_amount) if order.total_amount is not None else 0.0
            )
            logger.info(
                f"Latest order found for client ID {client_id}: Order ID {order.pk}, Amount {amount}"
            )
            return [order.pk, amount]
        except Orders.DoesNotExist:
            logger.error(f"No orders found for client ID {client_id}.")
            return [None, None]

    def create_payment_transaction(
        self, transaction_data: CreateTransactionDTO
    ) -> PaymentTransactionDTO:
        """Create a new payment transaction record.
        Args:
            transaction_data (CreateTransactionDTO): The data required to create a new payment transaction.
        Returns:
            PaymentTransactionDTO: A DTO containing the details of the created payment transaction.
        Raises:
            ValueError: If the transaction data is invalid or missing required fields.
        """
        transaction_model = PaymentTransaction.objects.create(
            client_id=transaction_data.client_id,
            order_id=transaction_data.order_id,
            amount=transaction_data.amount,
            transaction_ref=transaction_data.transaction_ref,
            gateway_name=transaction_data.gateway_name,
        )
        if not transaction_model:
            logger.error("Failed to create payment transaction.")
            raise ValueError("Failed to create payment transaction.")
        logger.info(f"Payment transaction created: {transaction_model.transaction_ref}")
        return PaymentTransactionDTO(
            id=transaction_model.pk,
            transaction_ref=transaction_model.transaction_ref,
            amount=float(transaction_model.amount),
            client_id=transaction_model.client_id,
            order_id=transaction_model.order_id,
            status=transaction_model.status,
            gateway_name=transaction_model.gateway_name,
            gateway_ref=transaction_model.gateway_ref,
        )

    def update_payment_transaction(
        self, transaction_id: Any, update_data: UpdateTransactionDTO
    ) -> PaymentTransactionDTO:
        """Update an existing payment transaction record.
        Args:
            transaction_id (Any): The unique identifier of the payment transaction to update.
            update_data (UpdateTransactionDTO): The data to update the payment transaction with.
        Returns:
            PaymentTransactionDTO: A DTO containing the updated details of the payment transaction.
        Raises:
            PaymentTransaction.DoesNotExist: If the payment transaction with the given ID does not exist.
        """
        try:
            transaction_model = PaymentTransaction.objects.get(pk=transaction_id)

            # Update model fields from the update_data DTO
            if update_data.status is not None:
                transaction_model.status = update_data.status
            if update_data.gateway_ref is not None:
                transaction_model.gateway_ref = update_data.gateway_ref
            if update_data.amount is not None:
                transaction_model.amount = update_data.amount

            transaction_model.save()
            logger.info(
                f"Payment transaction updated: {transaction_model.transaction_ref}"
            )
            return PaymentTransactionDTO(
                id=transaction_model.pk,
                transaction_ref=transaction_model.transaction_ref,
                amount=float(transaction_model.amount),
                client_id=transaction_model.client_id,
                order_id=transaction_model.order_id,
                status=transaction_model.status,
                gateway_name=transaction_model.gateway_name,
                gateway_ref=transaction_model.gateway_ref,
            )
        except PaymentTransaction.DoesNotExist:
            logger.error(
                f"Payment transaction with ID {transaction_id} does not exist."
            )
            return None
