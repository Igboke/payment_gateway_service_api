from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import BankTransferSerializers
from utils import get_client_by_mail
from .core_logic import PaymentDetails

class InitiatePaymentView(APIView):
    """
    This is an Initiate payment API function, simply for requests and response
    """
    def post(self,request,*args,**kwargs):
        #pass request data to serializer for validaton and conversion to Python data types
        serializer = BankTransferSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Extract the validated data
        client = get_client_by_mail(validated_data["email"])

        if not client:
            return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)

        



        pass

