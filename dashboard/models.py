from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import datetime

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # Add more fields as necessary

    def __str__(self):
        return self.name 

class Tag(models.Model):
    name = models.CharField(max_length=100)
    # Add more fields as necessary

    def __str__(self):
        return self.name 

class Item(models.Model):
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    in_stock = models.BooleanField(default=True)
    available_stock = models.DecimalField(max_digits=10, decimal_places=2)
    # Add additional fields and methods as necessary

    def __str__(self):
        return self.name + ' ' + str(self.category)
    
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_set",
        related_query_name="custom_user",
    )

    reset_password_token = models.CharField(max_length=100, blank=True, null=True)
    reset_password_token_expiration = models.DateTimeField(blank=True, null=True)

    def set_password_reset_token(self, token):
        self.reset_password_token = token
        self.reset_password_token_expiration = datetime.datetime.now() + datetime.timedelta(hours=1)
        self.save()

    def clear_password_reset_token(self):
        self.reset_password_token = None
        self.reset_password_token_expiration = None
        self.save()

    # Add custom fields here, if needed

    def __str__(self):
        return self.username
    
    