import logging
import requests
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import BankTransferSerializers, BankTransferOutputSerializers  
from .services import initiate_payment, update_model_from_webhook
import traceback


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HandleWebhookView(APIView):
    """
    API endpoint to handle webhooks
    """
    @extend_schema(
        request=None,
        responses={200: {"description": "Webhook processed successfully."},
            400: {"description": "Bad Request (e.g., invalid payload, missing signature)."},
            401: {"description": "Unauthorized (e.g., invalid signature)."},
            404: {"description": "Transaction not found."},
            500: {"description": "Internal Server Error."}
        },
        summary="Handle Webhook",
        description="Handles incoming webhook notifications from the payment gateway."
    )
    def post(self,request,*args,**kwargs):
        #request at this point is not coming from the serializer field rather from flutterwave(payment gateway) its best to return 200 as documentation 
        data = request.data
        logging.info(f"Received webhook data: {data}")
        # Call the service function to handle the webhook
        try:
            response_dto = update_model_from_webhook(data)
            if not response_dto:
                return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(response_dto, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(ValueError(str(e)), status=status.HTTP_400_BAD_REQUEST)

class InitiatePaymentView(APIView):
    """
    API endpoint to initiate a payment.
    """
    @extend_schema(
        request=BankTransferSerializers,
        responses={200: BankTransferOutputSerializers},
        summary="Perform Bank Transfers",
        description="Perform Bank Transfers using FLutterWave"
    )
    def post(self, request, *args, **kwargs):
        serializer = BankTransferSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            # Call the service function to initiate payment
            output_response_dict = initiate_payment(validated_data)
            output_serializer = BankTransferOutputSerializers(output_response_dict)
            return Response(output_serializer.data, status=status.HTTP_200_OK)

        
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except requests.exceptions.RequestException as e:
            
            return Response({"error": "Payment gateway communication error:", "detail":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print("An exception occurred:")
            traceback.print_exc()
            return Response({"error": "An internal error occurred", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            