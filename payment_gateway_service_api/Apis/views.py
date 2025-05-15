import requests
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import BankTransferSerializers, BankTransferOutputSerializers  
from .services import initiate_payment

class HandleWebhookView(APIView):
    """
    API endpoint to handle webhooks
    """
    def post(self,request,*args,**kwargs):
        #request at this point is not coming from the serializer field rather from flutterwave(payment gateway) its best to return 200 as documentation 
        data = request.data
        
        pass

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
            import traceback
            print("An exception occurred:")
            traceback.print_exc()
            return Response({"error": "An internal error occurred", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            


# will add a webhook endpoint view similar to InitiatePaymentView
# It would parse raw request body, create adapters/core, call payment_service.handle_gateway_webhook,
# and return a 200 OK response if successful (as webhooks expect).