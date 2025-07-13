from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount , SocialToken
from django.shortcuts import redirect
import json
import urllib.parse

#Google Auth
@login_required
def google_login_callback(request):
    user = request.user

    social_accounts = SocialAccount.objects.filter(user=user)
    print("Social Account for user:", social_accounts)

    social_account = social_accounts.first()

    if not social_account:
        print("No social account for user:", user)
        return redirect('http://localhost:5173/login/callback/?error=NoSocialAccount')
    
    token = SocialToken.objects.filter(account=social_account, account__provider='google').first()

    if token:
        print('Google token found:', token.token)
        refresh = RefreshToken.for_user(user)
        user_data = {
            'id': user.id,
            'email': user.email,
            'username': getattr(user, 'username', '') or user.email.split('@')[0],
        }
        tokens = {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
        payload = {
            'user': user_data,
            'tokens': tokens
        }
        encoded_data = urllib.parse.quote(json.dumps(payload))

        return redirect(f'http://localhost:5173/login/callback/?data={encoded_data}')
    else:
        print('No Google token found for user', user)
        return redirect(f'http://localhost:5173/login/callback/?error=NoGoogleToken')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def google_account_status(request):
    
    has_google_account = SocialAccount.objects.filter(
        user=request.user,
        provider='google'
    ).exists()
    return Response({
        'has_google_account': has_google_account
    })

def connect_google_account(request):
    return redirect('/accounts/google/login/?process=connect/')


