from django.shortcuts import render

#from django.http import JsonResponse
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .serializers import ConfirmEmailSerializer
import requests


# from djoser.views import

class UserActivationView(APIView):
    def get(self, request, uid, token):
        protocol = 'https://' if request.is_secure() else 'http://'
        web_url = protocol + request.get_host()
        post_url = web_url + "/auth/users/activation/"
        post_data = {'uid': uid, 'token': token}
        result = requests.post(post_url, data=post_data)
        content = result.text
        return Response(content)


class ConfirmEmailView(GenericAPIView):
    serializer_class = ConfirmEmailSerializer
    token_generator = default_token_generator

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.email_confirmed = True
        user.save()
        return Response(status=status.HTTP_202_ACCEPTED)


class PostToConfirmEmail(APIView):
    def get(self, request, uid, token):
        protocol = 'https://' if request.is_secure() else 'http://'
        web_url = protocol + request.get_host()
        post_url = web_url + "/auth/user/confirmation/"
        post_data = {'uid': uid, 'token': token}
        result = requests.post(post_url, data=post_data)
        content = result.text
        return Response(content)

