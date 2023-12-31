from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

# Create your models here.
class CustomUser(AbstractUser):
    # Add any additional fields if needed
    # For example: profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    currency = models.IntegerField(default=0)
    transaction_history = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.username}"
    
class Coin(models.Model):
    name = models.CharField(max_length=100)
    amount = models.IntegerField(default=0)
    value = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.amount}"
    
class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    coins = models.ManyToManyField(Coin, through='CoinBalance')

    def __str__(self):
        return f"Wallet of {self.user.username}"

class CoinBalance(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=10)

    def __str__(self):
        return f"{self.coin.name} - {self.amount}"
    

class Transaction(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"
    
class Card(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    number = models.CharField(max_length=16) # Assuming a 16-digit card number
    cardholder_name = models.CharField(max_length=100)
    expiration_date = models.CharField(max_length=5)  # Storing date as 'MM/YY'
    CVV = models.CharField(max_length=4)  # CVV/CVC security code

    def clean(self):
        # Custom validation to check the format of expiration_date
        if len(self.expiration_date) != 5 or not self.expiration_date[:2].isdigit() or not self.expiration_date[2] == '/' or not self.expiration_date[3:].isdigit():
            raise ValidationError('Expiration date should be in MM/YY format')

    def __str__(self):
        return f"{self.cardholder_name}'s Card - **** **** **** {self.number[-4:]}"


