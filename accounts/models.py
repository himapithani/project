from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        AGENT = "AGENT", "Support Agent"
        CUSTOMER = "CUSTOMER", "Customer"

    role = models.CharField(
        max_length=16,
        choices=Roles.choices,
        default=Roles.CUSTOMER,
    )
    preferred_language = models.CharField(max_length=10, default="en")

    def is_admin(self):
        return self.role == self.Roles.ADMIN or self.is_superuser
