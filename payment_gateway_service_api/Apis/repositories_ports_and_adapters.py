from abc import ABC, abstractmethod
from typing import Optional, Any
from dataclasses import dataclass
from django.contrib.auth import get_user_model
from Orders.models import PaymentTransaction, Orders 

@dataclass
class ClientDTO:
    id: Any 
    email: str
    full_name: str
    

@dataclass
class PaymentTransactionDTO:
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
    client_id: Any
    order_id: Any
    amount: float
    transaction_ref: str
    gateway_name: Optional[str] = None

@dataclass
class UpdateTransactionDTO:
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
    def create_payment_transaction(self, transaction_data: CreateTransactionDTO) -> PaymentTransactionDTO:
        """Create a new payment transaction record."""
        pass

    @abstractmethod
    def update_payment_transaction(self, transaction_id: Any, update_data: UpdateTransactionDTO) -> PaymentTransactionDTO:
        """Update an existing payment transaction record."""
        pass

    @abstractmethod
    def get_latest_order_and_amount_for_client(self, client_id: Any) -> list[int|None]:
         """Get the ID/details and amount of the client's latest order."""
         pass
    

ClientModel = get_user_model()

class DjangoClientRepositoryAdapter(ClientRepositoryInterface):

    def get_client_by_email(self, email: str) -> Optional[ClientDTO]:
        try:
            client_model = ClientModel.objects.get(email=email)
            # Translate Django model to core DTO
            return ClientDTO(
                id=client_model.pk,
                email=client_model.email,
                full_name=client_model.get_full_name()
            )
        except ClientModel.DoesNotExist:
            return None
        
    def get_transaction_by_id(self, transaction_ref):
        transaction_model = PaymentTransaction.objects.get(transaction_ref=transaction_ref)
        if not transaction_model:
            raise ValueError("Transaction reference not found in the webhook data")
        return transaction_model.pk

    def get_latest_order_and_amount_for_client(self, client_id: Any) -> list[int|None]:
         try:
             order = Orders.objects.filter(client_id=client_id).latest('created_at')
             amount = float(order.total_amount) if order.total_amount is not None else 0.0
             return [order.pk, amount]
         except Orders.DoesNotExist:
             return [None, None]

    def create_payment_transaction(self, transaction_data: CreateTransactionDTO) -> PaymentTransactionDTO:
        transaction_model = PaymentTransaction.objects.create(
            client_id=transaction_data.client_id,
            order_id=transaction_data.order_id,
            amount=transaction_data.amount,
            transaction_ref=transaction_data.transaction_ref,
            gateway_name=transaction_data.gateway_name
        )
        
        return PaymentTransactionDTO(
            id=transaction_model.pk,
            transaction_ref=transaction_model.transaction_ref,
            amount=float(transaction_model.amount),
            client_id=transaction_model.client_id,
            order_id=transaction_model.order_id,
            status=transaction_model.status,
            gateway_name=transaction_model.gateway_name,
            gateway_ref=transaction_model.gateway_ref
        )

    def update_payment_transaction(self, transaction_id: Any, update_data: UpdateTransactionDTO) -> PaymentTransactionDTO:
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

            
            return PaymentTransactionDTO(
                id=transaction_model.pk,
                transaction_ref=transaction_model.transaction_ref,
                amount=float(transaction_model.amount),
                client_id=transaction_model.client_id,
                order_id=transaction_model.order_id,
                status=transaction_model.status,
                gateway_name=transaction_model.gateway_name,
                gateway_ref=transaction_model.gateway_ref
            )
        except PaymentTransaction.DoesNotExist:             
            return None