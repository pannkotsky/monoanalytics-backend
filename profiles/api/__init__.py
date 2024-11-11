from django.conf import settings

from drf_spectacular.utils import extend_schema
from drf_standardized_errors.openapi_serializers import ErrorResponse429Serializer
from rest_framework import exceptions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from data_imports.exceptions import ImportException
from data_providers.monobank import MonobankPersonalProvider
from data_providers.provider_base import ProviderBase
from profiles.models import Account, Profile


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "id",
            "is_active",
            "balance",
            "credit_limit",
            "type",
            "currency_code",
            "masked_pan",
            "iban",
            "last_updated",
            "statement_last_updated",
        ]
        read_only_fields = fields


class ProfileSerializer(serializers.ModelSerializer):
    accounts = AccountSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "name", "last_updated", "accounts"]
        read_only_fields = fields


class ProfileImportMonobankBasicSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True, required=True)


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_queryset(self):
        # TODO: enforce row level security on database level and using django-guardian
        return (
            super()
            .get_queryset()
            .filter(user=self.request.user)
            .order_by("-last_updated", "-id")
        )

    def import_base(
        self,
        request,
        provider: ProviderBase,
        input_serializer_class: type[serializers.Serializer],
    ):
        user = request.user
        serializer = input_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            profile = provider.import_profile(serializer.validated_data, user.id)
        except ImportException as e:
            detail = str(e)
            if e.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                raise exceptions.Throttled(detail=detail)
            if e.status_code < status.HTTP_500_INTERNAL_SERVER_ERROR:
                raise exceptions.ValidationError(detail)
            raise exceptions.APIException(detail)

        if not user.first_name and not user.last_name:
            last_name, first_name = profile.name.split(" ", 1)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        return Response(ProfileSerializer(profile).data)

    @extend_schema(
        request=ProfileImportMonobankBasicSerializer,
        responses={
            200: ProfileSerializer,
            429: ErrorResponse429Serializer,
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="import/monobank-personal",
        url_name="import-monobank-personal",
        permission_classes=[IsAuthenticated],
    )
    def import_monobank_personal(self, request):
        if not settings.DATA_PROVIDERS["MONOBANK_PERSONAL"]["ENABLED"]:
            raise exceptions.NotFound(detail="Provider not found")
        return self.import_base(
            request, MonobankPersonalProvider(), ProfileImportMonobankBasicSerializer
        )
