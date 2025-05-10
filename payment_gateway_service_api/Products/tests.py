from django.test import TestCase
from .models import Products

class ProductsModelTest(TestCase):
    """
    Test case for the Products model.
    """
    def setUp(self):
        """"
        Set up a product instance for testing.
        """
        self.product_1 = Products.objects.create(
            name="Test Product 1",
            quantity=10,
            description="Test Description 1",
            price=99.99,
        )
        self.product_2 = Products.objects.create(
            name= "Test Product 2",
            quantity=0,
            description="Test Description 2",
            price=49.99,
            is_available = False,
        )
        # self.product_3 = Products.objects.create(
        #     name = "Invalid Test Product 3",
        #     quantity = -10,
        #     description = "Invalid Test Description 3",
        #     price = 19.99,
        # )
    def test_product_creation(self):
        """
        Test the creation of a product.
        """
        self.assertEqual(self.product_1.name, "Test Product 1")
        self.assertEqual(self.product_1.quantity, 10)
        self.assertEqual(self.product_1.description, "Test Description 1")
        self.assertEqual(self.product_1.price, 99.99)
        self.assertTrue(self.product_1.is_available)

