import logging
import requests
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import BankTransferSerializers, BankTransferOutputSerializers
from .services import initiate_payment, update_model_from_webhook
import traceback


logger = logging.getLogger(__name__)


class HandleWebhookView(APIView):
    """
    API endpoint to handle webhooks from the payment gateway.
    This view processes incoming webhook notifications, validates the payload,
    and updates the payment transaction model accordingly.
    It expects the webhook data to be in the request body and handles
    various response statuses based on the outcome of the processing.
    The view is designed to be flexible and can handle different payment gateways
    by using the appropriate service function to update the model based on the webhook data.
    """

    @extend_schema(
        request=None,
        responses={
            200: {"description": "Webhook processed successfully."},
            400: {
                "description": "Bad Request (e.g., invalid payload, missing signature)."
            },
            401: {"description": "Unauthorized (e.g., invalid signature)."},
            404: {"description": "Transaction not found."},
            500: {"description": "Internal Server Error."},
        },
        summary="Handle Webhook",
        description="Handles incoming webhook notifications from the payment gateway.",
    )
    def post(self, request, *args, **kwargs):
        """
        Handles incoming webhook notifications from the payment gateway.
        This method processes the webhook data, validates it, and updates the
        payment transaction model accordingly. It returns appropriate HTTP responses
        based on the outcome of the processing.
        Args:
            request: The HTTP request object containing the webhook data.
        Returns:
            Response: A DRF Response object with the status of the processing.
        """
        data = request.data
        logger.info(f"Received webhook data: {data}")

        try:
            response_dto = update_model_from_webhook(data)
            if not response_dto:
                logger.warning("Transaction not found for the provided reference.")
                return Response(
                    {"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND
                )
            logger.info("Webhook processed successfully.")
            return Response(response_dto, status=status.HTTP_200_OK)
        except ValueError as e:
            logger.error(f"ValueError occurred: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class InitiatePaymentView(APIView):
    """
    API endpoint to initiate a payment.
    This view accepts payment details via a POST request,
    validates the input, and processes the payment through the payment gateway.
    It returns the payment transaction reference and gateway response upon success,
    or appropriate error messages in case of failure.
    """

    @extend_schema(
        request=BankTransferSerializers,
        responses={200: BankTransferOutputSerializers},
        summary="Perform Bank Transfers",
        description="Perform Bank Transfers using FLutterWave",
    )
    def post(self, request, *args, **kwargs):
        """
        Initiates a payment using the provided bank transfer details.
        This method validates the incoming request data, processes the payment
        through the payment gateway, and returns the transaction reference and
        gateway response if successful. It handles various exceptions and returns
        appropriate error messages for different failure scenarios.
        Args:
            request: The HTTP request object containing the payment details.
        Returns:
            Response: A DRF Response object with the payment transaction reference
                      and gateway response on success, or an error message on failure.
        """
        serializer = BankTransferSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:

            output_response_dict = initiate_payment(validated_data)
            output_serializer = BankTransferOutputSerializers(output_response_dict)
            logger.info(
                f"Payment initiated successfully: {output_response_dict['transaction_ref']}"
            )
            return Response(output_serializer.data, status=status.HTTP_200_OK)

        except ValueError as e:
            logger.error(f"ValueError occurred: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except requests.exceptions.RequestException as e:
            logger.error(f"Payment gateway communication error: {str(e)}")
            return Response(
                {"error": "Payment gateway communication error:", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {"error": "An internal error occurred", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
