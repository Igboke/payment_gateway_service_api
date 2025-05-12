from dataclasses import dataclass
from payment_gateway_service_api.Apis.payments_ports_and_adapters import GatewayProcessPaymentResponseDTO, PaymentDetails, PaymentGatewayInterface
from payment_gateway_service_api.Apis.repositories_ports_and_adapters import ClientRepositoryInterface
from utils import ClientPaymentDetails, get_client_by_mail

# DTOs used by the core itself or passed to ports
@dataclass
class InitialPaymentRequestDTO:
    client_email: str
    amount: float
    currency: str
    is_permanent: bool = False

@dataclass
class InitiatedPaymentResponseDTO: # Output from the core's initiate_payment method
    transaction_ref: str
    gateway_response: GatewayProcessPaymentResponseDTO
     
class PaymentServiceCore:
    def __init__(self,gateway_adapter: PaymentGatewayInterface,client_repository: ClientRepositoryInterface):
        self.gateway_adapter = gateway_adapter
        self.client_repository = client_repository

    def initiate_payment(self,payment_details: PaymentDetails) -> dict:
        self.client = get_client_by_mail(PaymentDetails.client_email)
        client_payment_transaction_instance = ClientPaymentDetails(self.client).set_transaction_model()
        payment_details.tx_ref = client_payment_transaction_instance.transaction_ref
        payment_details.amount = client_payment_transaction_instance.amount
        payment_details.client_email = self.client.email
        payment_details.client_name = self.client.get_full_name()
        payment_details.currency = "NGN"
        self.gateway_adapter.process_payment(payment_details,client_payment_transaction_instance)
        #update payment model here
        