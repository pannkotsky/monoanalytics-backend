# Generated by Django 5.1.3 on 2024-11-11 09:34

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MerchantCategory",
            fields=[
                (
                    "code",
                    models.IntegerField(
                        primary_key=True,
                        serialize=False,
                        validators=[django.core.validators.MaxValueValidator(9999)],
                    ),
                ),
                ("description", models.CharField(blank=True, max_length=512)),
                ("description_ua", models.CharField(blank=True, max_length=512)),
            ],
            options={
                "verbose_name_plural": "Merchant categories",
            },
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="StatementItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("id_from_provider", models.CharField(max_length=64)),
                ("time", models.DateTimeField()),
                ("description", models.CharField(max_length=256)),
                ("hold", models.BooleanField(default=False)),
                ("amount_in_account_currency", models.IntegerField()),
                ("amount_in_operation_currency", models.IntegerField()),
                (
                    "currency_code",
                    models.IntegerField(
                        validators=[django.core.validators.MaxValueValidator(999)]
                    ),
                ),
                ("commission_rate", models.IntegerField()),
                ("cashback_amount", models.IntegerField()),
                ("balance", models.IntegerField()),
                ("counter_name", models.CharField(blank=True, max_length=256)),
                ("raw_data", models.JSONField()),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="statement_items",
                        to="profiles.account",
                    ),
                ),
                (
                    "merchant_category",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="statement_items",
                        to="statement.merchantcategory",
                    ),
                ),
                (
                    "tags",
                    models.ManyToManyField(
                        related_name="statement_items", to="statement.tag"
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("id_from_provider", "account"),
                        name="unique_statement_item",
                    )
                ],
            },
        ),
    ]
