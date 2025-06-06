from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth import get_user_model
from clients.utils import Address
import logging

logger = logging.getLogger(__name__)


class ClientManager(BaseUserManager):
    """
    Override the default basemanger to account for changes to the default usermodel
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return user with email and password
        """
        if not email:
            logger.error("Email is required, email must be set")
            raise ValueError("Email is required, email must be set")

        # normalize mail-(lowercasing-emails are case insensitive), trimming white space and handling some specific domains like gmail
        email = self.normalize_email(email)

        ClientModel = get_user_model()

        client = ClientModel(email=email, **extra_fields)
        client.set_password(password)
        client.save(using=self._db)

        return client

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with designated fields
        Since i would be calling on create_user(), only thing that needs to be done is setting the extra fields
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            logger.error("Super User must have is_staff set to True")
            raise ValueError("Super User must have is_staff set to True")
        if extra_fields.get("is_superuser") is not True:
            logger.error("Super User must have is_superuser set to True")
            raise ValueError("Super User must have is_superuser set to True")
        if extra_fields.get("is_active") is not True:
            logger.error("Super user must have is_active set to True")
            raise ValueError("Super user must have is_active set to True")
        if not email:
            logger.error("Email must be set, No email available")
            raise ValueError("Email must be set, No email available")

        return self.create_user(email, password, **extra_fields)


class Client(AbstractUser):
    """
    Client inherits from the Abstract user class. this is to set the username to be field
    """

    username = models.CharField(max_length=150, unique=False, null=True, blank=True)
    email = models.EmailField(null=False, unique=True, help_text="Enter mail")
    last_name = models.CharField(max_length=50, help_text="Enter Surname")
    first_name = models.CharField(max_length=50, help_text="Enter First Name")
    middle_name = models.CharField(
        max_length=50, null=True, help_text="Enter Optional middle name"
    )
    house_address = models.ForeignKey(
        Address, on_delete=models.PROTECT, related_name="client"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    objects = ClientManager()

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.email
