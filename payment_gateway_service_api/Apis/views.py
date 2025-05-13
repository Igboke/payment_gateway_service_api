import requests
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .payments_ports_and_adapters import FlutterWaveAdapter
from .repositories_ports_and_adapters import DjangoClientRepositoryAdapter
from .serializers import BankTransferSerializers, BankTransferOutputSerializers 
from .core_logic import PaymentServiceCore, InitialPaymentRequestDTO 

class InitiatePaymentView(APIView):
    """
    API endpoint to initiate a payment.
    """
    @extend_schema(
        request=BankTransferSerializers,
        responses={200: BankTransferOutputSerializers},
        summary="",
        description=""
    )
    def post(self, request, *args, **kwargs):
        serializer = BankTransferSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Instantiate the concrete adapters
        payment_gateway_adapter = FlutterWaveAdapter()
        client_repo_adapter = DjangoClientRepositoryAdapter()

        # Instantiate the core service, injecting the adapters
        payment_service = PaymentServiceCore(
            gateway_adapter=payment_gateway_adapter,
            client_repository=client_repo_adapter
        )

        try:
            # Prepare input DTO for the core service
            initial_request_dto = InitialPaymentRequestDTO(
                client_email=validated_data["email"],
                amount=validated_data["amount"],
                currency=validated_data["currency"],
                is_permanent=validated_data.get("is_permanent", False),
                payment_gateway_name="FlutterWave"
            )

            # Call the core service method
            response_dto = payment_service.initiate_payment(initial_request_dto)

            # Prepare the HTTP response based on the core's output DTO
            output_response_dict = {
                "transaction_ref":response_dto.transaction_ref,
                "gateway_response":response_dto.gateway_response.raw_response
            }
            output_serializer = BankTransferOutputSerializers(output_response_dict)
            return Response(output_serializer.data, status=status.HTTP_200_OK)

        
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except requests.exceptions.RequestException as e:
            
            return Response({"error": "Payment gateway communication error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": "An internal error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# will add a webhook endpoint view similar to InitiatePaymentView
# It would parse raw request body, create adapters/core, call payment_service.handle_gateway_webhook,
# and return a 200 OK response if successful (as webhooks expect).