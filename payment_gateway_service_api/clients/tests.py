from django.test import TestCase
from django.contrib.auth import get_user_model
from .utils import Address
from django.db.utils import IntegrityError
from django.db.models import ProtectedError


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
            postal_code="10001",
        )

        self.client_1 = get_user_model().objects.create_user(
            email="danieligboke669@gmail.com",
            last_name="Igboke",
            first_name="Daniel",
            password="password123",
            house_address=self.Address_1,
        )

    def test_client_creation(self):
        self.assertEqual(self.client_1.email, "danieligboke669@gmail.com")
        self.assertEqual(self.client_1.house_address.street_line1, "Bourdillion 1234")

    def test_create_user_no_email_fails(self):
        with self.assertRaises(ValueError) as context:
            get_user_model().objects.create_user(
                email=None,
                password="testpassword",
                last_name="Invalid",
                first_name="User",
                house_address=self.Address_1,
            )
        self.assertIn("Email is required, email must be set", str(context.exception))

    def test_client_str(self):
        self.assertEqual(str(self.client_1), self.client_1.email)

    def test_unique_email(self):
        with self.assertRaises(IntegrityError) as context:
            get_user_model().objects.create_user(
                email=self.client_1.email,
                password="anotherpassword123",
                last_name="Doe",
                first_name="John",
                house_address=self.Address_1,
            )
        self.assertIn("unique constraint", str(context.exception).lower())

    def test_full_name_func(self):
        full_name = f"{self.client_1.first_name} {self.client_1.last_name}"
        self.assertEqual(self.client_1.get_full_name(), full_name)

    def test_optional_fields_can_be_null_or_empty(self):
        client_optional = get_user_model().objects.create_user(
            email="optionaluser@example.com",
            password="password123",
            last_name="Optional",
            first_name="User",
            house_address=self.Address_1,
            username=None,  # Testing null=True
            middle_name="",  # Testing blank=True (might save as None if null=True)
        )
        self.assertIsNone(client_optional.username)
        self.assertTrue(
            client_optional.middle_name is None or client_optional.middle_name == ""
        )

        # Or simply test creating without providing them
        client_no_optional = get_user_model().objects.create_user(
            email="nooptional@example.com",
            password="password123",
            last_name="No",
            first_name="Optional",
            house_address=self.Address_1,
        )
        self.assertIsNone(client_no_optional.username)
        self.assertTrue(
            client_no_optional.middle_name is None
            or client_no_optional.middle_name == ""
        )

    def test_address_protects_client_deletion(self):
        # Attempt to delete the Address object that self.client_1 is linked to
        with self.assertRaises(ProtectedError) as context:
            self.Address_1.delete()
        self.assertIsInstance(context.exception, ProtectedError)

        print(context.exception)
        self.assertIn("Cannot delete some instances of model", str(context.exception))

    def test_username_field_is_email(self):
        self.assertEqual(get_user_model().USERNAME_FIELD, "email")
