from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model set as AUTH_USER_MODEL from the first migration."""
