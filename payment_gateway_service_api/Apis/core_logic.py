from dataclasses import dataclass
from ports_and_adapters import PaymentGatewayInterface
from utils import ClientPaymentDetails, get_client_by_mail

@dataclass
class PaymentDetails:
    tx_ref: str
    amount: float
    currency: str
    client_email: str
    client_name: str
    is_permanent: bool = False

class PaymentServiceCore:
    def __init__(self,gateway_adapter: PaymentGatewayInterface):
        self.gateway_adapter = gateway_adapter

    def initiate_payment(self,payment_details: PaymentDetails) -> dict:
        self.client = get_client_by_mail(PaymentDetails.client_email)
        client_payment_transaction_instance = ClientPaymentDetails(self.client).set_transaction_model()
        payment_details.tx_ref = client_payment_transaction_instance.transaction_ref
        payment_details.amount = client_payment_transaction_instance.amount
        payment_details.client_email = self.client.email
        payment_details.client_name = self.client.get_full_name()
        payment_details.currency = "NGN"
        self.gateway_adapter.process_payment(payment_details,client_payment_transaction_instance)
        