from typing import Dict, Any
from .payments_ports_and_adapters import FlutterWaveAdapter
from .repositories_ports_and_adapters import DjangoClientRepositoryAdapter
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