from django.utils.translation import gettext_lazy as _

from dj_rest_auth.registration.serializers import (
    RegisterSerializer as DjRestAuthRegisterSerializer,
)
from rest_framework import generics, serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email"]


class UserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        return self.request.user


class RegisterSerializer(DjRestAuthRegisterSerializer):
    def validate_email(self, email):
        email = super().validate_email(email)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                _("A user is already registered with this email address."),
            )
        return email
