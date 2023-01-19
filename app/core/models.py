"""
DB models
"""

from django.conf import settings
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

        # ** seems to be equal to ... operator in JS/TS,
        #   like function (...args) {}
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

    # override the built-in username field with email
    #   (which is originally username)
    USERNAME_FIELD = 'email'

# models.Model is the base class provided by django
# which means it's just using the default format


class Recipe(models.Model):
    # recipe object
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,

        # CASCADE simply means
        # if this user object is deleted from the db
        # all the recipe objects related to this user
        # will also be deleted
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.title


class Tag(models.Model):
    # tag for filtering recipes

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    # returns the string representation
    # that we're checking for in the test
    def __str__(self):
        return self.name
