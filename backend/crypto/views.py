from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm, SignInForm, CardForm
from django.contrib.auth.decorators import login_required
import requests
from .models import CustomUser, Card, Transaction, Wallet, Coin, CoinBalance
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import HttpResponse, JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sessions.models import Session
import jwt
from django.contrib import messages
from datetime import datetime, timedelta
from django.conf import settings
from django.urls import reverse
from urllib.parse import urlencode
from django.db.models import Sum
from django.shortcuts import get_object_or_404

def operate_crypto_view(request):
    token = request.GET.get('token', None)

    if token is None:
        return JsonResponse({'error': 'Token not provided in the URL'}, status=401)

    try:
        return render(request, 'crypto_operations.html')
        
          # Successful response
        
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return JsonResponse({'error': 'Invalid or expired token'}, status=401)


@login_required
def buy_crypto(request):
    crypto_symbols = ['bitcoin', 'ethereum', 'tether']  # Add more cryptocurrencies if needed

    # Fetch prices for the specified cryptocurrencies
    prices = {}
    for symbol in crypto_symbols:
       price = get_crypto_price(symbol)
       prices[symbol] = price

    context = {
           'prices': prices
    }
    if request.method == 'POST':
            user_wallet = Wallet.objects.get(user=request.user)
            # Get the deposit amount from the form data
            deposit_amount = float(request.POST.get('amount', 0))  # Assuming 'amount_usd' is the input name
            if request.user.currency < deposit_amount:
                messages.error(request, "Insufficient funds")
                return render(request, 'buy.html', context) # Redirect to the buy coins page or any other page
            cryptocoin = request.POST.get('crypto', 0)
            # Perform actions based on user_id or other token information
            # Cryptocurrencies you want to fetch prices for
            # Update the user's currency with the   deposit amount
            price = get_crypto_price(str(cryptocoin).lower())
            new_currency = deposit_amount/price
            coin = Coin(name=cryptocoin, amount=new_currency, value=price)
            coin.save()
            coin_balance, created = CoinBalance.objects.get_or_create(
                wallet=user_wallet,
                coin=coin,
                defaults={'amount': new_currency}  # Update this with the calculated amount
            )
            if not created:
                coin_balance.amount += new_currency
                coin_balance.save()
            #coin = Coin(name=symbols[cryptocoin],amount=deposit_amount,value=price)
            transaction = Transaction(user=request.user, amount=deposit_amount, transaction_type='buy')
            transaction.save()
            request.user.currency -= deposit_amount
            request.user.save()
    return render(request, 'buy.html', context)

def view_wallet(request):
    user_wallet = Wallet.objects.get(user=request.user)
    
    # Grouping coins by name and summing their amounts
    coin_balances = (
        CoinBalance.objects.filter(wallet=user_wallet).values('coin__name').annotate(total_amount=Sum('amount'))
    )

    return render(request, 'view_wallet.html', {'user_wallet': user_wallet, 'coin_balances': coin_balances})


@login_required
def deposit_view(request):
    token = request.GET.get('token', None)

    if token is None:
        return JsonResponse({'error': 'Token not provided in the URL'}, status=401)

    try:

        user_cards = Card.objects.filter(user=request.user)
        if request.method == 'POST':
            if not user_cards:
                messages.error(request, "No card")
                return render(request, 'deposit.html', {'user_cards': user_cards}) # Redirect to the buy coins page or any other page
            # Get the deposit amount from the form data
            deposit_amount = float(request.POST.get('amount_usd', 0))  # Assuming 'amount_usd' is the input name

            # Update the user's currency with the deposit amount
            user = request.user  # Get the current logged-in user
            user.currency += deposit_amount  # Add the deposit amount to the user's currency
            user.save()
            transaction = Transaction(user=request.user, amount=deposit_amount, transaction_type='deposit')
            transaction.save()

            return redirect('user_info')  # Redirect to a success page or any other page after deposit

        return render(request, 'deposit.html', {'user_cards': user_cards})
        
          # Successful response
        
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return JsonResponse({'error': 'Invalid or expired token'}, status=401)

def landing_page(request):
    return render(request, 'landing_page.html')

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            Wallet.objects.create(user=user)
            payload = {
                    'username': username,
                    'exp': datetime.utcnow() + timedelta(days=1),  # Token expiration time
                    'iat': datetime.utcnow()  # Time when the token is generated
            }
                
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            print(token)

            #jwt_token = token.decode('utf-8') 
            #print(jwt_token)  
            token_url = reverse('user_info') + '?' + urlencode({'token': token})


            # Redirect to user_info view after token generation
            return redirect(token_url)  # Redirect to your user_info URL name
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})



def sign_in(request):
    if request.method == 'POST':
        form = SignInForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                # Authenticate user session
                login(request, user)

                payload = {
                    'username': username,
                    'exp': datetime.utcnow() + timedelta(days=1),  # Token expiration time
                    'iat': datetime.utcnow()  # Time when the token is generated
                }
                
                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                print(token)

                #jwt_token = token.decode('utf-8') 
                #print(jwt_token)  
                token_url = reverse('user_info') + '?' + urlencode({'token': token})


                # Redirect to user_info view after token generation
                return redirect(token_url)  # Redirect to your user_info URL name
    else:
        form = SignInForm()
    return render(request, 'signin.html', {'form': form})


@login_required
def user_info(request):
    user = request.user  # Fetch the logged-in user
    context = {'user': user}
    return render(request, 'user_info.html', context)
    


def get_crypto_price(symbol):
    base_url = "https://api.coingecko.com/api/v3"
    endpoint = f"/simple/price?ids={symbol}&vs_currencies=usd"  # Replace 'usd' with the currency you want the price in

    url = f"{base_url}{endpoint}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        price = data[symbol]['usd']  # Replace 'usd' with the currency you specified earlier
        return price
    else:
        # Handle the error
        return None



def send_cryp(request):
    user_wallet = Wallet.objects.get(user=request.user)
    coin_balances = (
        CoinBalance.objects.filter(wallet=user_wallet).values('coin__name').annotate(total_amount=Sum('amount'))
    )
    if request.method == 'POST':
            sender = request.user
            receiver_identifier = request.POST.get('receiver')
            coin_name = request.POST.get('crypto')
            amount_to_send = float(request.POST.get('amount', 0))

            # Fetch sender's specific coin balance, assuming a single coin balance exists for the user and coin
            sender_coin_balance = get_object_or_404(CoinBalance, wallet__user=sender, coin__name=coin_name)

            if sender_coin_balance.amount >= amount_to_send:
                try:
                    receiver = CustomUser.objects.get(username=receiver_identifier)
                except CustomUser.DoesNotExist:
                    messages.error(request, "Receiver does not exist.")
                    return redirect('send_coins')

                sender_coin_balance.amount -= amount_to_send
                sender_coin_balance.save()

                transaction_sender = Transaction(user=sender, amount=-amount_to_send, transaction_type='send', coin=coin_name)
                transaction_sender.save()

                receiver_coin_balance, created = CoinBalance.objects.get_or_create(wallet__user=receiver, coin__name=coin_name)
                receiver_coin_balance.amount += amount_to_send
                receiver_coin_balance.save()

                transaction_receiver = Transaction(user=receiver, amount=amount_to_send, transaction_type='receive', coin=coin_name)
                transaction_receiver.save()

                messages.success(request, f"You have successfully sent {amount_to_send} {coin_name} to {receiver_identifier}!")
                return redirect('send_coins')
            else:
                messages.error(request, "Insufficient balance.")
                return redirect('send_coins')
    return render(request, "send.html", {'user_wallet': user_wallet, 'coin_balances': coin_balances})

@login_required
def check_history(request):
    user_transactions = Transaction.objects.filter(user=request.user)
    return render(request, 'history.html', {'user_transactions': user_transactions})

@login_required
def add_card(request):
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            new_card = form.save(commit=False)
            new_card.user = request.user  # Assign the card to the logged-in user
            new_card.save()
            return redirect('add_card')  # Redirect to a page showing user's cards
    else:
        form = CardForm()
    
    return render(request, 'add_card.html', {'form': form})

@login_required
def user_cards(request):
    user_cards = Card.objects.filter(user=request.user)
    return render(request, 'user_cards.html', {'user_cards': user_cards})

@login_required
def select_card_for_deposit(request):
    user_cards = Card.objects.filter(user=request.user)
    
    if request.method == 'POST':
        selected_card_id = request.POST.get('selected_card')
        selected_card = Card.objects.get(id=selected_card_id)
        # Process the selected card for deposit (perform deposit logic here)
        # Redirect or render a success message
        return render(request, 'deposit.html')
        
    return render(request, 'select_card.html', {'user_cards': user_cards})
