from django.forms import ValidationError
from django.test import TestCase
from .models import Products, Orders, OrderItem, Address
from django.contrib.auth import get_user_model


class OrdersTestCase(TestCase):
    """
    Test case for the Orders model
    """

    def setUp(self):
        self.address = Address.objects.create(
            street_line1="Bourdillion Street",
            street_line2="Bourdillion Avenue",
            city="Ikoyi",
            state_province="Lagos",
            postal_code="101233",
            country="USA",
        )
        self.client_1 = get_user_model().objects.create_user(
            email="danieligboke669@gmail.com",
            password="password123",
            first_name="Daniel",
            last_name="Igboke",
            house_address=self.address,
        )

        self.product = Products.objects.create(
            name="Test Product",
            quantity=10,
            description="Test Description",
            price=100.00,
            is_available=True,
        )
        self.order_1 = Orders.objects.create(
            client=self.client_1,
            status="pending",
            total_amount=0.00,
            shipping_address=self.address,
            billing_address=self.address,
        )

    def test_product_creation(self):
        """
        Test the creation of a product
        """
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.quantity, 10)
        self.assertEqual(self.product.description, "Test Description")
        self.assertEqual(self.product.price, 100.00)
        self.assertTrue(self.product.is_available)

    def test_order_creation(self):
        """
        Test the creation of an order
        """
        self.assertEqual(self.order_1.client, self.client_1)
        self.assertEqual(self.order_1.status, "pending")
        self.assertEqual(self.order_1.total_amount, 0)
        self.assertEqual(self.order_1.shipping_address, self.address)
        self.assertEqual(self.order_1.billing_address, self.address)

    def test_order_item_creation(self):
        """
        Test the creation of an order item
        """
        self.order_item = OrderItem.objects.create(
            product=self.product, order=self.order_1, quantity=2
        )
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.order, self.order_1)
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(OrderItem.objects.count(), 1)

    def test_order_item_str(self):
        """
        Test the string representation of an order item
        """
        self.order_item = OrderItem.objects.create(
            product=self.product, order=self.order_1, quantity=2
        )
        self.assertEqual(str(self.order_item), str(self.order_item.pk))

    def test_quantity_min_value_validator(self):
        """
        Test that quantity must be at least 1
        """
        order_item = OrderItem(product=self.product, order=self.order_1, quantity=0)

        with self.assertRaises(ValidationError) as context:
            order_item.full_clean()

        self.assertIn("quantity", context.exception.message_dict)
        self.assertIn(
            "Ensure this value is greater than or equal to 1.",
            context.exception.message_dict["quantity"][0],
        )

        # Attempt to create an OrderItem with negative quantity
        order_item_negative = OrderItem(
            product=self.product, order=self.order_1, quantity=-5
        )
        with self.assertRaises(ValidationError) as context:
            order_item_negative.full_clean()

        self.assertIn("quantity", context.exception.message_dict)
        self.assertIn(
            "Ensure this value is greater than or equal to 1.",
            context.exception.message_dict["quantity"][0],
        )
