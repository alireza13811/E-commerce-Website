from django.urls import path, include, re_path

from .views import GoogleCallBackView, GoogleLogin, GoogleAuthentication, ConfirmationEmailView
from dj_rest_auth.views import PasswordResetConfirmView


urlpatterns = [
    re_path(r'^registration/confirm-email/(?P<key>[-:\w]+)/$', ConfirmationEmailView.as_view()),
    path('registration/', include('dj_rest_auth.registration.urls')),
    re_path(r'^social/google/callback/', GoogleCallBackView.as_view()),
    path('social/google/login/', GoogleLogin.as_view(), name='google_login'),
    path('social/google/authentication/', GoogleAuthentication.as_view()),
    re_path(r'^password/reset/confirm/(?P<uidb64>[-:\w]+)/(?P<token>[-:\w]+)/$',
            PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
