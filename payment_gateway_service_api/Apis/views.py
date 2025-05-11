from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

class InitiatePaymentView(APIView):
    """
    This is an Initiate payment API function, simply for requests and response
    """
    def post(self,request,*args,**kwargs):
        #pass request data to serializer for validaton and conversion to Python data types

        pass

