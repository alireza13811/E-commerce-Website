from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
import urllib.parse
from django.shortcuts import redirect
from rest_framework.views import APIView


class GoogleCallBackView(APIView):

    def get(self, request, *args, **kwargs):

        # params = urllib.parse.
        code = str(request.GET['code'])
        protocol = 'https://' if request.is_secure() else 'http://'
        web_url = protocol + request.get_host()
        post_url = web_url + "/auth/social/google/"
        post_data = {"code": code}
        # result = requests.post(post_url, data=post_data)
        # file = open('a.html','w')
        # content = result.text
        # file.write(content)
        # file.close()
        print(code)
        return redirect(post_url, post_data)


class GoogleLogin(SocialLoginView):  # if you want to use Authorization Code Grant, use this
    authentication_classes = []
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:8000/auth/social/google/callback/"
    client_class = OAuth2Client

    # def get_serializer(self, *args, **kwargs):
    #     serializer_class = self.get_serializer_class()
    #     kwargs['context'] = self.get_serializer_context()
    #     return serializer_class(*args, **kwargs)
    #

