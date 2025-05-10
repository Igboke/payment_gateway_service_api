from django.test import TestCase
from django.contrib.auth import get_user_model
from .utils import Address
from django.db.utils import IntegrityError

class ClientModelTest(TestCase):
    """
    Test case for the Client model
    """
    def setUp(self):
        self.Address_1 = Address.objects.create(
            street_line1="Bourdillion 1234",
            street_line2="Bourdillion 4B",
            city="Ikoyi",
            state_province="Lagos",
            country="Nigeria",
            postal_code="10001"
        )

        self.client_1 = get_user_model().objects.create_user(
            email="danieligboke669@gmail.com",
            last_name="Igboke",
            first_name="Daniel",
            password="password123",
            house_address=self.Address_1,
        )
    def test_client_creation(self):
        self.assertEqual(self.client_1.email,"danieligboke669@gmail.com")
        self.assertEqual(self.client_1.house_address.street_line1,"Bourdillion 1234")

    def test_client_str(self):
        self.assertEqual(str(self.client_1),self.client_1.email)

    def test_unique_email(self):
        with self.assertRaises(IntegrityError) as context:
            get_user_model().objects.create_user(
                email=self.client_1.email,
                password="anotherpassword123",
                last_name="Doe",
                first_name="John",
                house_address=self.Address_1,
            )
        self.assertEqual(str(context.exception), "UNIQUE constraint failed: clients_client.email")

    def test_full_name_func(self):
        full_name = f"{self.client_1.first_name} {self.client_1.last_name}"
        self.assertEqual(self.client_1.get_full_name(), full_name)
