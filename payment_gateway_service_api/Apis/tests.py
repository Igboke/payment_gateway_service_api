"""
Tests
"""

import uuid
from unittest.mock import Mock, patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from clients.utils import Address

from .core_logic import (
    PaymentServiceCore,
    InitialPaymentRequestDTO,
    InitiatedPaymentResponseDTO,
)
from .payments_ports_and_adapters import (
    PaymentGatewayInterface,
    GatewayProcessPaymentResponseDTO,
)
from .repositories_ports_and_adapters import (
    ClientRepositoryInterface,
    ClientDTO,
    CreateTransactionDTO,
    PaymentTransactionDTO,
)
from Orders.models import Orders, PaymentTransaction


ClientModel = get_user_model()


# 1. TEST THE CORE LOGIC IN ISOLATION: We use Mock objects that conform to our Port interfaces.
class PaymentServiceCoreTests(TestCase):

    def setUp(self):
        # Create MOCK implementations of our ports (interfaces)
        self.mock_gateway_adapter = Mock(spec=PaymentGatewayInterface)
        self.mock_client_repository = Mock(spec=ClientRepositoryInterface)

        self.payment_service = PaymentServiceCore(
            gateway_adapter=self.mock_gateway_adapter,
            client_repository=self.mock_client_repository,
        )

    def test_initiate_payment_success(self):
        """
        Test the successful payment initiation flow within the core logic.
        """

        client_email = "test@example.com"

        mock_client = ClientDTO(id=1, email=client_email, full_name="Test User")
        self.mock_client_repository.get_client_by_email.return_value = mock_client

        latest_order_id = 101
        order_amount = 5000.00
        self.mock_client_repository.get_latest_order_and_amount_for_client.return_value = [
            latest_order_id,
            order_amount,
        ]

        initial_transaction_ref = str(uuid.uuid4())
        initial_transaction_dto = PaymentTransactionDTO(
            id=1,
            transaction_ref=initial_transaction_ref,
            amount=order_amount,
            client_id=1,
            order_id=latest_order_id,
            status="pending",
        )
        self.mock_client_repository.create_payment_transaction.return_value = (
            initial_transaction_dto
        )

        gateway_response_dto = GatewayProcessPaymentResponseDTO(
            success=True, gateway_ref="gw_ref_123", raw_response={"status": "success"}
        )
        self.mock_gateway_adapter.process_payment.return_value = gateway_response_dto

        final_transaction_dto = PaymentTransactionDTO(
            id=1,
            transaction_ref=initial_transaction_ref,
            amount=order_amount,
            client_id=1,
            order_id=latest_order_id,
            status="pending",
            gateway_ref="gw_ref_123",
        )
        self.mock_client_repository.update_payment_transaction.return_value = (
            final_transaction_dto
        )

        request_dto = InitialPaymentRequestDTO(
            client_email=client_email,
            currency="NGN",
            payment_gateway_name="MockGateway",
        )
        response = self.payment_service.initiate_payment(request_dto)

        self.assertIsInstance(response, InitiatedPaymentResponseDTO)
        self.assertEqual(response.transaction_ref, initial_transaction_ref)
        self.assertTrue(response.gateway_response.success)

        self.mock_client_repository.get_client_by_email.assert_called_once_with(
            client_email
        )
        self.mock_client_repository.get_latest_order_and_amount_for_client.assert_called_once_with(
            mock_client.id
        )
        self.mock_client_repository.create_payment_transaction.assert_called_once()
        self.mock_gateway_adapter.process_payment.assert_called_once()
        self.mock_client_repository.update_payment_transaction.assert_called_once()

    def test_initiate_payment_client_not_found(self):
        """
        Test that initiating payment fails if the client doesn't exist.
        """

        self.mock_client_repository.get_client_by_email.return_value = None

        request_dto = InitialPaymentRequestDTO(
            client_email="notfound@example.com",
            currency="NGN",
            payment_gateway_name="MockGateway",
        )

        with self.assertRaises(ValueError) as context:
            self.payment_service.initiate_payment(request_dto)

        self.assertIn(
            "Client with email notfound@example.com not found", str(context.exception)
        )


class PaymentAPITests(APITestCase):
    """
    TEST THE API ENDPOINTS (INTEGRATION TESTS)
    We test the Views and Serializers using DRF's APITestCase.
    We will PATCH the service function (`initiate_payment`) to isolate the view.
    """

    def setUp(self):

        self.address = Address.objects.create(city="Test City", country="TC")
        self.user = ClientModel.objects.create_user(
            email="api_user@example.com",
            password="password123",
            first_name="API",
            last_name="User",
            house_address=self.address,
        )
        self.order = Orders.objects.create(
            client=self.user,
            total_amount=1500.00,
            shipping_address=self.address,
            billing_address=self.address,
        )
        self.initiate_payment_url = reverse("create-payment")
        self.webhook_url = reverse("webhook")

        self.client.force_authenticate(user=self.user)

    @patch("Apis.views.initiate_payment")
    def test_initiate_payment_api_success(self, mock_initiate_payment):
        """
        Test the POST /api/payments/v1/createpayment/ endpoint for a successful scenario.
        """

        # Configure the mock service to return a successful-looking dictionary
        transaction_ref = str(uuid.uuid4())
        mock_response = {
            "transaction_ref": transaction_ref,
            "gateway_response": {"status": "success", "message": "Transfer Queued"},
        }
        mock_initiate_payment.return_value = mock_response

        request_data = {"email": "api_user@example.com", "currency": "NGN"}

        response = self.client.post(
            self.initiate_payment_url, request_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["transaction_ref"], transaction_ref)
        self.assertIn("gateway_response", response.data)

        # Verify the service function was called with the validated data
        mock_initiate_payment.assert_called_once_with(
            {"email": "api_user@example.com", "currency": "NGN", "is_permanent": False}
        )

    @patch("Apis.views.initiate_payment")
    def test_initiate_payment_api_client_not_found(self, mock_initiate_payment):
        """
        Test the createpayment endpoint when the service layer raises a ValueError.
        """

        # Configure the mock service to simulate an error
        mock_initiate_payment.side_effect = ValueError(
            "Client not found in service layer"
        )

        request_data = {"email": "nonexistent@example.com", "currency": "NGN"}

        response = self.client.post(
            self.initiate_payment_url, request_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Client not found in service layer")

    @patch("Apis.views.update_model_from_webhook")
    def test_webhook_handler_api_success(self, mock_update_model):
        """
        Test the POST /api/payments/v1/webhook/ endpoint.
        """

        mock_update_model.return_value = {
            "status": "Success",
            "message": "Transaction updated",
        }

        webhook_payload = {
            "event": "charge.completed",
            "data": {"id": 12345, "tx_ref": "some-tx-ref", "status": "successful"},
        }

        response = self.client.post(self.webhook_url, webhook_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "Success")

        # Verify our mocked service function was called with the payload
        mock_update_model.assert_called_once_with(webhook_payload)
