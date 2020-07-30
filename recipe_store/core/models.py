from django.db import models
# imports required to extend the Django USer model
# while making use of some of the features that come with django user model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
# User_Manager class: provides helper function for creating a user/superuser


class UserManager(BaseUserManager):
    """
    **extra_fields : can take more fields that are passed in during user model creation
    Not required, gives flexibility to our user model, incase we add new fields to user model
    they do not need to be added here explicitly in the create_user() parameters
    """

    def create_user(self, email, password=None, **extra_fields):
        """Creates and save a new user"""
        # ValueWrror for empty email field
        if not email:
            raise ValueError('Users must have an email address')
        # The extra fields are unwind here
        # Access the user model by the UserManager using self.model,
        # effectively same as creating new user model object and it's assignment
        # self.normalize_email(email) - makes the domain name lowercase comes with the BaseUserManager module
        user = self.model(email=self.normalize_email(email), **extra_fields)
        # password is not stored in clear text and is encrypted so it cannot be set the same way as user
        user.set_password(password)  # comes with AbstractBaseUser
        user.save(using=self._db)  # helps with multiple DB, not required but good practice

        return user

    def create_superuser(self, email, password):
        """Create a super user and save it"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user
# Lets create the user models extending AbstractBaseUser and PermissionsMixin(args, kwargs)
# These modules give us all the features that come out of the box with the django user model
# But we can then build on top of them and customize it to support our email


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    # add the USERNAME_FIELD to be email instead of username
    USERNAME_FIELD = 'email'
    # configure the User model in settings.py using AUTH_USER_MODEL


class Tag(models.Model):
    """Tag to be used for a recipe - str give tag.name"""
    name = models.CharField(max_length=255)
    # best practic: retrieve the authuser model settings from settings.py
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient to be used in a recipe - str gives ingredient.name"""
    name = models.CharField(max_length=255)
    # best practic: retrieve the authuser model settings from settings.py
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe made by users with tags and ingredients"""
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    link = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title
