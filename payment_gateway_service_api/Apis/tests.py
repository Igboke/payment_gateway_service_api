"""
Tests
"""

import uuid
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import Mock, patch

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
from clients.utils import Address

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
