from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from currencies.utils import get_letter_code


class Profile(models.Model):
    mono_id = models.CharField(max_length=64)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profiles"
    )
    token = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    last_updated = models.DateTimeField(null=True, blank=True)
    raw_data = models.JSONField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "mono_id"], name="unique_profile_mono_id"
            ),
            models.UniqueConstraint(
                fields=["user", "token"], name="unique_profile_token"
            ),
            models.UniqueConstraint(
                fields=["user", "name"], name="unique_profile_name"
            ),
        ]

    def __str__(self):
        return self.name


class Account(models.Model):
    class AccountType(models.TextChoices):
        BLACK = "black", _("Black")
        WHITE = "white", _("White")
        PLATINUM = "platinum", _("Platinum")
        IRON = "iron", _("Iron")
        FOP = "fop", _("Private Entrepreneur")
        YELLOW = "yellow", _("Yellow")
        EAID = "eAid", _("e-Aid")
        MADE_IN_UKRAINE = "madeInUkraine", _("Made in Ukraine")

    class CashbackType(models.TextChoices):
        UAH = "UAH", _("UAH")
        MILES = "Miles", _("Miles")

    mono_id = models.CharField(max_length=64)
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="accounts"
    )
    is_active = models.BooleanField(default=True)
    balance = models.IntegerField()
    credit_limit = models.IntegerField()
    type = models.CharField(max_length=14, choices=AccountType.choices)
    currency_code = models.IntegerField(validators=[MaxValueValidator(999)])
    cashback_type = models.CharField(
        max_length=5, choices=CashbackType.choices, blank=True, null=True
    )
    masked_pan = models.CharField(max_length=19)
    iban = models.CharField(max_length=34)
    last_updated = models.DateTimeField(null=True, blank=True)
    statement_last_updated = models.DateTimeField(null=True, blank=True)
    raw_data = models.JSONField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "mono_id"], name="unique_account_mono_id"
            ),
        ]

    def __str__(self):
        return f"{self.profile} {self.get_type_display()} {self.masked_pan} {get_letter_code(self.currency_code)}"


class Jar(models.Model):
    mono_id = models.CharField(max_length=64)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="jars")
    title = models.CharField(max_length=64)
    description = models.TextField()
    currency_code = models.IntegerField(validators=[MaxValueValidator(999)])
    balance = models.IntegerField()
    goal = models.IntegerField(null=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    raw_data = models.JSONField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "mono_id"], name="unique_jar_mono_id"
            ),
        ]

    def __str__(self):
        return f"{self.profile} - {self.title}"
