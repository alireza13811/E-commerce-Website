from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer, \
    UidAndTokenSerializer
from djoser.conf import settings
from django.core import exceptions


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'password',
                  'email', 'first_name', 'last_name']


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ConfirmEmailSerializer(UidAndTokenSerializer):
    default_error_messages = {
        "stale_token": settings.CONSTANTS.messages.STALE_TOKEN_ERROR
    }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.user.is_active:
            return attrs
        raise exceptions.PermissionDenied(self.error_messages["stale_token"])
