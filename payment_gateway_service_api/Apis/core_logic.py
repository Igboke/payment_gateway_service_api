from dataclasses import dataclass
from ports_and_adapters import PaymentGatewayInterface

@dataclass
class PaymentDetails:
    tx_ref: str
    amount: float
    currency: str
    client_email: str
    client_name: str
    is_pemanent: bool = False

class PaymentServiceCore:
    def __init__(self,gateway_adapter: PaymentGatewayInterface):
        self.gateway_adapter = gateway_adapter

    def initiate_payment(self,payment_details: PaymentDetails) -> dict:
        self.gateway_adapter.process_payment(payment_details)
        pass