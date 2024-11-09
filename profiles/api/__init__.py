from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from profiles.import_utils import ImportError, import_profile
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
            "cashback_type",
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


class ProfileImportDataSerializer(serializers.Serializer):
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

    @action(detail=False, methods=["post"], url_path="import", url_name="import")
    def import_(self, request):
        user = request.user
        serializer = ProfileImportDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = import_profile(user.id, serializer.validated_data["token"])
        except ImportError as e:
            return Response({"non_field_errors": [str(e)]}, status=e.status_code)

        if not user.first_name and not user.last_name:
            last_name, first_name = profile.name.split(" ", 1)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        return Response(ProfileSerializer(profile).data)
