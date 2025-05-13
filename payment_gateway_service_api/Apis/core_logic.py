from dataclasses import dataclass
import uuid
from .payments_ports_and_adapters import GatewayProcessPaymentResponseDTO, PaymentDetails, PaymentGatewayInterface
from .repositories_ports_and_adapters import ClientRepositoryInterface, CreateTransactionDTO, UpdateTransactionDTO

# DTOs used by the core itself or passed to ports
@dataclass
class InitialPaymentRequestDTO:
    client_email: str
    currency: str
    payment_gateway_name:str
    is_permanent: bool = False
    amount: float = 0.0
    

@dataclass
class InitiatedPaymentResponseDTO: # Output from the core's initiate_payment method
    transaction_ref: str
    gateway_response: GatewayProcessPaymentResponseDTO
     
class PaymentServiceCore:
    def __init__(self,gateway_adapter: PaymentGatewayInterface,client_repository: ClientRepositoryInterface):
        self.gateway_adapter = gateway_adapter
        self.client_repository = client_repository

    def initiate_payment(self, request_data: InitialPaymentRequestDTO) -> InitiatedPaymentResponseDTO:
        """
        Initiates a payment process for a client.
        """
        client = self.client_repository.get_client_by_email(request_data.client_email)
        
        if not client:           
            raise ValueError(f"Client with email {request_data.client_email} not found")

        latest_order_id,amount = self.client_repository.get_latest_order_and_amount_for_client(client.id)
        if not latest_order_id:
            raise ValueError(f"No order found for client {client.id}")

        transaction_ref = str(uuid.uuid4()) 

        create_transaction_dto = CreateTransactionDTO(
            client_id=client.id,
            order_id=latest_order_id,
            amount=amount,
            transaction_ref=transaction_ref,
            gateway_name=request_data.payment_gateway_name,
            
        )
        
        initial_transaction = self.client_repository.create_payment_transaction(create_transaction_dto)


        
        payment_details_for_gateway = PaymentDetails( 
            tx_ref=initial_transaction.transaction_ref,
            amount=initial_transaction.amount, 
            currency=request_data.currency,
            client_email=client.email,
            client_name=client.full_name,
            is_permanent=request_data.is_permanent
        )

        gateway_response_dto = self.gateway_adapter.process_payment(payment_details_for_gateway)

        update_transaction_dto = UpdateTransactionDTO(
            id=initial_transaction.id,
            gateway_ref=gateway_response_dto.gateway_ref,
            status="pending" if gateway_response_dto.success else "failed"
             
        )
        updated_transaction = self.client_repository.update_payment_transaction(initial_transaction.id, update_transaction_dto)

        return InitiatedPaymentResponseDTO(
            transaction_ref=updated_transaction.transaction_ref,
            gateway_response=gateway_response_dto,
        )
        