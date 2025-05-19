from typing import Dict, Any
import random
from .payments_ports_and_adapters import FlutterWaveAdapter, PayStackAdapter
from .repositories_ports_and_adapters import DjangoClientRepositoryAdapter
from .core_logic import PaymentServiceCore, InitialPaymentRequestDTO

def initiate_payment(validated_data) -> Dict[str, Any]:
    """
    Initiates a payment process for a client. FOllowing SRP
    """
    # Instantiate the concrete adapters
    if random.random() < 0.5:
        payment_gateway_adapter = PayStackAdapter()
        payment_gateway_name = "PayStack"
    else:
        payment_gateway_adapter = FlutterWaveAdapter()
        payment_gateway_name = "FlutterWave"
    
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
                payment_gateway_name=payment_gateway_name
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
    payment_gateway_adapter = FlutterWaveAdapter()
    client_repo_adapter = DjangoClientRepositoryAdapter()
    # Instantiate the core service, injecting the adapters
    payment_service = PaymentServiceCore(
        gateway_adapter=payment_gateway_adapter,
        client_repository=client_repo_adapter
    )

    try:
        # Call the core service method to handle the webhook
        payment_transaction_dto=payment_service.update_model_from_webhook(request_data)
        if payment_transaction_dto:
            response = {
                "message":"Successfully updated model",
                "status":"Success"
            }
        else:
            response={
                "message":"Transaction model not found",
                "status":"Failed"
            }

        return response

    except ValueError as e:
        raise ValueError(str(e))