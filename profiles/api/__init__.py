from rest_framework import serializers, viewsets

from profiles.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "name", "last_updated"]
        read_only_fields = fields


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
