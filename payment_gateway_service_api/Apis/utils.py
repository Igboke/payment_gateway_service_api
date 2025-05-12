from django.contrib.auth import get_user_model
import uuid
from Orders.models import PaymentTransaction, Orders

ClientModel = get_user_model()

class ClientPaymentDetails:
    """
    Client Payment Details
    This class is used to handle payment transaction details for a client.
    """
    def __init__(self, client):
        self.client = client
        self.transaction_reference = None
        self.amount = None
        self.payment_status = None

    def set_transaction_model(self)-> PaymentTransaction:
        """
        - order: pk 
        - client: pk
        - amount: decimal 
        - status : string, not implemented here
        - transaction_ref: str, unique
        - gateway_ref: not implemented here
        - gateway_name: str, Bank Transfer default, updated later 
        """
        PaymentTransaction.objects.create(
            order=self.get_transaction_order(),
            client=self.client.pk,
            amount=self.get_payment_amount(),
            transaction_ref=self.generate_transaction_reference(),
            gateway_name="Bank Transfer"
        )

    def get_transaction_order(self):
        """
        Get the latest Transaction Order
        """
        try:
            order = Orders.objects.filter(client=self.client).latest('created_at')
            return order.pk
        except Orders.DoesNotExist:
            return None


    def get_payment_amount(self):
        """
        Get Payment Amount
        """
        try:
            order = Orders.objects.filter(client=self.client).latest('created_at')
            self.amount = order.total_amount
            return self.amount
        except Orders.DoesNotExist:
            return None
        
    def generate_transaction_reference(self):
        """
        Generate Transaction Reference using standard uuid.uuid4()
        """
        # Generate a unique transaction reference using UUID
        return str(uuid.uuid4())

def get_client_by_mail(email):
    """
    Get Client by Email
    """
    try:
        client = ClientModel.objects.get(email=email)
        return client
    except ClientModel.DoesNotExist:
        return None
    


    
