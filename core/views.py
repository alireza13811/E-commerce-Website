from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from rest_framework.views import APIView
from django.conf import settings
from dj_rest_auth.registration.views import ConfirmEmailView


class GoogleCallBackView(APIView):

    def get(self, request, *args, **kwargs):
        code = str(request.GET['code'])
        json_obj = {"code": code}
        return Response(json_obj, status=status.HTTP_202_ACCEPTED)


class GoogleLogin(SocialLoginView):
    authentication_classes = []
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.SOCIAL_AUTH_GOOGLE_REDIRECT_URI
    client_class = OAuth2Client


class GoogleAuthentication(APIView):
    def get(self, request):
        return redirect(
            f'https://accounts.google.com/o/oauth2/v2/auth?redirect_uri={settings.SOCIAL_AUTH_GOOGLE_REDIRECT_URI}'
            f'&prompt=consent&response_type=code&client_id={settings.SOCIAL_AUTH_GOOGLE_OAUTH2_ID} '
            f'&scope=openid%20email%20profile')


class ConfirmationEmailView(ConfirmEmailView):
    def post(self, *args, **kwargs):
        confirmation = self.get_object()
        user = confirmation.email_address.user
        user.email_confirmed = True
        user.save()
        redirect_url = self.get_redirect_url()
        if not redirect_url:
            ctx = self.get_context_data()
            return self.render_to_response(ctx)
        return redirect(redirect_url)
