from typing import Dict, Any
import random
from .payments_ports_and_adapters import FlutterWaveAdapter, PayStackAdapter
from .repositories_ports_and_adapters import DjangoClientRepositoryAdapter
from .core_logic import PaymentServiceCore, InitialPaymentRequestDTO
import logging

logger = logging.getLogger(__name__)


def initiate_payment(validated_data) -> Dict[str, Any]:
    """
    Initiates a payment process for a client. FOllowing SRP
    principle, this function is responsible for initiating the payment process
    by interacting with the payment gateway and client repository adapters.
    """

    if random.random() < 0.5:
        payment_gateway_adapter = PayStackAdapter()
        payment_gateway_name = "PayStack"
    else:
        payment_gateway_adapter = FlutterWaveAdapter()
        payment_gateway_name = "FlutterWave"

    client_repo_adapter = DjangoClientRepositoryAdapter()

    payment_service = PaymentServiceCore(
        gateway_adapter=payment_gateway_adapter, client_repository=client_repo_adapter
    )

    try:
        initial_request_dto = InitialPaymentRequestDTO(
            client_email=validated_data["email"],
            currency=validated_data["currency"],
            is_permanent=validated_data.get("is_permanent", False),
            payment_gateway_name=payment_gateway_name,
        )

        response_dto = payment_service.initiate_payment(initial_request_dto)

        output_response_dict = {
            "transaction_ref": response_dto.transaction_ref,
            "gateway_response": response_dto.gateway_response.raw_response,
        }
        logger.info(
            f"Payment initiated successfully: {output_response_dict['transaction_ref']}"
        )
        return output_response_dict

    except ValueError as e:
        logger.error(f"Error initiating payment: {str(e)}")
        return {"error": str(e)}


def update_model_from_webhook(request_data):
    """
    Handles updating data using information gotten from the payment gateway webhook.
    This function determines which payment gateway adapter to use based on the
    presence of a transaction reference in the request data. It then uses the
    appropriate adapter to update the payment transaction model in the database.
    This function follows the Single Responsibility Principle (SRP) by focusing
    solely on updating the model from the webhook data, without mixing in other
    responsibilities such as initiating payments or handling business logic.
    """
    transaction_ref = request_data.get("data", {}).get("tx_ref", "")
    if transaction_ref:
        payment_gateway_adapter = FlutterWaveAdapter()
    else:
        payment_gateway_adapter = PayStackAdapter()
    client_repo_adapter = DjangoClientRepositoryAdapter()

    payment_service = PaymentServiceCore(
        gateway_adapter=payment_gateway_adapter, client_repository=client_repo_adapter
    )

    try:

        payment_transaction_dto = payment_service.update_model_from_webhook(
            request_data
        )
        if payment_transaction_dto:
            logger.info(
                f"Successfully updated model from webhook for transaction: {transaction_ref}"
            )
            response = {"message": "Successfully updated model", "status": "Success"}
        else:
            logger.warning(
                f"Transaction model not found for transaction reference: {transaction_ref}"
            )
            response = {"message": "Transaction model not found", "status": "Failed"}

        return response

    except ValueError as e:
        logger.error(f"Error updating model from webhook: {str(e)}")
        raise ValueError(str(e)) from e
