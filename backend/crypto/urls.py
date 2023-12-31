from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('signup/', views.sign_up, name='signup'),  
    path('signin/', views.sign_in, name='signin'),
    path('', views.landing_page, name='landing_page'),
    path('user/', views.user_info, name='user_info'),
    path('user/deposit/',views.deposit_view, name="deposit_view"),
    path('user/send', views.send_cryp, name="send_cryp"),
    path('user/buy', views.buy_crypto, name="buy_crypto"),
    path('user/history', views.check_history, name="check_history"),
    path('user/add-card/', views.add_card, name='add_card'),
    path('user/cards/', views.user_cards, name='user_cards'),
    path('user/select-card',views.select_card_for_deposit, name="select_card_for_deposit"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/crypto-operations/',views.operate_crypto_view, name='operate_crypto_view'),
    path('user/wallet/',views.view_wallet, name='view_wallet'),
    # Other URLs and views...
]
