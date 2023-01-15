"""
DB models
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    # manager for users
    def create_user(self, email, password=None, **extra_fields):
        # create, save and return a new user

        # ** seems to be equal to ... operator in JS/TS, like function (...args) {}
        if not email:
            raise ValueError('Email is required')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)  # creates an encrypted password
        user.save(using=self._db)  # can also save this data to multiple DBs

        return user

    def create_superuser(self, email, password):
        # create and return a new superuser
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)

        return user


# AbstractBaseUser: functionality for auth system
# PermissionsMixin: functionality for the permissions and fields
class User(AbstractBaseUser, PermissionsMixin):
    # user in the system
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # sign in with django admin

    objects = UserManager()  # assigning the manager

    # override the built-in username field with email (which is originally username)
    USERNAME_FIELD = 'email'
