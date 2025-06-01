from django.test import TestCase
from .models import Products


class ProductsModelTest(TestCase):
    """
    Test case for the Products model.
    """

    def setUp(self):
        """ "
        Set up a product instance for testing.
        """
        self.product_1 = Products.objects.create(
            name="Test Product 1",
            quantity=10,
            description="Test Description 1",
            price=99.99,
        )
        self.product_2 = Products.objects.create(
            name="Test Product 2",
            quantity=0,
            description="Test Description 2",
            price=49.99,
            is_available=False,
        )

    def test_product_creation(self):
        """
        Test the creation of a product.
        """
        self.assertEqual(self.product_1.name, "Test Product 1")
        self.assertEqual(self.product_1.quantity, 10)
        self.assertEqual(self.product_1.description, "Test Description 1")
        self.assertEqual(self.product_1.price, 99.99)
        self.assertTrue(self.product_1.is_available)

    def test_product_str(self):
        """
        Test the string representation of a product.
        """
        self.assertEqual(str(self.product_1), "Test Product 1")
        self.assertEqual(str(self.product_2), "Test Product 2")

    def test_product_ordering(self):
        """
        Test the ordering of products by created_at.
        the list is then a list of products with oldest at 0 then 1 and so on
        """
        products = Products.objects.all()
        self.assertEqual(products[0], self.product_1)
        self.assertEqual(products[1], self.product_2)

    def test_product_constraints(self):
        """
        Test the constraints on the product model.
        """
        with self.assertRaises(Exception) as context:
            # Attempt to create a product with negative quantity
            Products.objects.create(
                name="Invalid Test Product 3",
                quantity=-10,
                description="Invalid Test Description 3",
                price=19.99,
            )

        self.assertEqual(
            str(context.exception),
            "CHECK constraint failed: quantity_greater_than_zero",
        )

    def test_product_availability(self):
        """
        Test the availability of a product.
        assert true is true if condition is true.
        assert false is true if condition is false
        """
        self.assertTrue(self.product_1.is_available)
        self.assertFalse(self.product_2.is_available)
