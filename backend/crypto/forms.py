from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Card

class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2', 'name', 'surname')  

class SignInForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password') 

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['number', 'cardholder_name', 'expiration_date', 'CVV']


