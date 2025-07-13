from django.urls import path
from .views import google_account_status, connect_google_account

urlpatterns = [
    path('google-account-status/', google_account_status, name='google_account_status'),
    path('connect-google-account/', connect_google_account, name='connect_google_account'),
]
