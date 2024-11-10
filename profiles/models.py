from datetime import datetime

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models

from currencies.utils import get_letter_code


class Profile(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profiles"
    )
    provider = models.ForeignKey(
        "data_imports.Provider", on_delete=models.CASCADE, related_name="profiles"
    )
    id_from_provider = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    last_updated = models.DateTimeField(auto_now=True)
    webhook_url = models.URLField(blank=True, default="")
    raw_data = models.JSONField(default=dict)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "provider", "id_from_provider"],
                name="unique_profile_id_from_provider",
            ),
            models.UniqueConstraint(
                fields=["user", "name"], name="unique_profile_name"
            ),
        ]

    def __str__(self):
        return self.name


class Account(models.Model):
    id_from_provider = models.CharField(max_length=64)
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="accounts"
    )
    is_active = models.BooleanField(default=True)
    balance = models.IntegerField()
    credit_limit = models.IntegerField()
    type = models.CharField(max_length=14)
    currency_code = models.IntegerField(validators=[MaxValueValidator(999)])
    masked_pan = models.CharField(max_length=19)
    iban = models.CharField(max_length=34, blank=True, default="")
    last_updated = models.DateTimeField(auto_now=True)
    raw_data = models.JSONField(default=dict)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "id_from_provider"],
                name="unique_account_id_from_provider",
            ),
        ]

    def __str__(self):
        return f"{self.profile} {self.type} {self.masked_pan} {get_letter_code(self.currency_code)}"

    @property
    def statement_last_updated(self) -> datetime | None:
        from data_imports.models.statement_import import StatementImport

        return (
            self.pk
            and StatementImport.objects.filter(
                account_id=self.pk,
                status=StatementImport.Status.FINISHED,
                finished_at__isnull=False,
            ).aggregate(models.Max("finished_at"))["finished_at__max"]
        )


class Jar(models.Model):
    id_from_provider = models.CharField(max_length=64)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="jars")
    title = models.CharField(max_length=64)
    description = models.TextField()
    currency_code = models.IntegerField(validators=[MaxValueValidator(999)])
    balance = models.IntegerField()
    goal = models.IntegerField(null=True)
    last_updated = models.DateTimeField(auto_now=True)
    raw_data = models.JSONField(default=dict)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "id_from_provider"],
                name="unique_jar_id_from_provider",
            ),
        ]

    def __str__(self):
        return f"{self.profile} - {self.title}"
