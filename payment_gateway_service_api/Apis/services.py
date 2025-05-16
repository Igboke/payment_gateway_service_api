from typing import Dict, Any
from .payments_ports_and_adapters import FlutterWaveAdapter
from Orders.models import PaymentTransaction
from .repositories_ports_and_adapters import DjangoClientRepositoryAdapter, UpdateTransactionDTO
from .core_logic import PaymentServiceCore, InitialPaymentRequestDTO

def initiate_payment(validated_data) -> Dict[str, Any]:
    """
    Initiates a payment process for a client. FOllowing SRP
    """
    # Instantiate the concrete adapters
    payment_gateway_adapter = FlutterWaveAdapter()
    client_repo_adapter = DjangoClientRepositoryAdapter()

    # Instantiate the core service, injecting the adapters
    payment_service = PaymentServiceCore(
        gateway_adapter=payment_gateway_adapter,
        client_repository=client_repo_adapter
    )

    try:
        initial_request_dto = InitialPaymentRequestDTO(
                client_email=validated_data["email"],
                currency=validated_data["currency"],
                is_permanent=validated_data.get("is_permanent", False),
                payment_gateway_name="FlutterWave"
            )
        
        # Call the core service method
        response_dto = payment_service.initiate_payment(initial_request_dto)

        output_response_dict = {
                "transaction_ref":response_dto.transaction_ref,
                "gateway_response":response_dto.gateway_response.raw_response
            }
        return output_response_dict

    except ValueError as e:
        return {"error": str(e)}
    
def update_model_from_webhook(request_data):
    """
    Handles updating data using information gotten from the payment gateway webhook. 
    """
    # Instantiate the concrete adapters
    client_repo_adapter = DjangoClientRepositoryAdapter()


    try:
        # Call the core service method to handle the webhook
        data = request_data.get("data", {})
        transaction_ref = data.get("tx_ref", "")
        if not transaction_ref:
            raise ValueError("Transaction reference not found in the webhook data")
        transaction_model = PaymentTransaction.objects.get(transaction_ref=transaction_ref)
        payment_id = transaction_model.id
        status = data.get("status", "")
        gateway_ref = data.get("flw_ref", "")
        amount = data.get("amount", 0.0)
        update_transaction_dto = UpdateTransactionDTO(
            id=payment_id,
            status=status,
            gateway_ref=gateway_ref,
            amount=amount
        )
        payment_transaction_dto = client_repo_adapter.update_payment_transaction(payment_id, update_transaction_dto)

        return True if payment_transaction_dto else False
    except PaymentTransaction.DoesNotExist:
        return False

    except ValueError as e:
        raise ValueError(str(e))