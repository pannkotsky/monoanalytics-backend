from django.utils.translation import gettext_lazy as _

from dj_rest_auth.registration.serializers import (
    RegisterSerializer as DjRestAuthRegisterSerializer,
)
from rest_framework import serializers

from users.models import User


class RegisterSerializer(DjRestAuthRegisterSerializer):
    def validate_email(self, email):
        email = super().validate_email(email)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                _("A user is already registered with this email address."),
            )
        return email
