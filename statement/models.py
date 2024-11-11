from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from profiles.models import Account
from .managers import StatementItemQuerySet


class MerchantCategory(models.Model):
    code = models.IntegerField(primary_key=True, validators=[MaxValueValidator(9999)])
    description = models.CharField(max_length=512, blank=True)
    description_ua = models.CharField(max_length=512, blank=True)

    class Meta:
        verbose_name_plural = _("Merchant categories")

    def __str__(self):
        return f"{self.code} {self.description}"


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class StatementItem(models.Model):
    id_from_provider = models.CharField(max_length=64)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="statement_items"
    )
    time = models.DateTimeField()
    description = models.CharField(max_length=256)
    merchant_category = models.ForeignKey(
        MerchantCategory,
        null=True,
        on_delete=models.SET_NULL,
        related_name="statement_items",
    )
    hold = models.BooleanField(default=False)
    amount_in_account_currency = models.IntegerField()
    amount_in_operation_currency = models.IntegerField()
    currency_code = models.IntegerField(validators=[MaxValueValidator(999)])
    commission_rate = models.IntegerField()
    cashback_amount = models.IntegerField()
    balance = models.IntegerField()
    counter_name = models.CharField(max_length=256, blank=True)
    raw_data = models.JSONField()
    tags = models.ManyToManyField(Tag, related_name="statement_items")

    objects = StatementItemQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["id_from_provider", "account"], name="unique_statement_item"
            )
        ]

    def __str__(self):
        return f"{self.time} {self.description}"
