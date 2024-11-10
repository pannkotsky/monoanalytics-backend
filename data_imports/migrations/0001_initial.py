# Generated by Django 5.1.1 on 2024-11-10 21:19

import data_imports.providers.monobank.providers
import typing
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Provider",
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
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "private_key",
                    models.CharField(blank=True, default="", max_length=255),
                ),
            ],
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="StatementImport",
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
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("finished", "Finished"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=255,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("imported_items_count", models.IntegerField(default=0)),
                ("error", models.TextField(blank=True, default="")),
            ],
        ),
        migrations.CreateModel(
            name="MonobankCorporateProvider",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=(
                data_imports.providers.monobank.providers.MonobankProviderBaseMixin,
                "data_imports.provider",
            ),
        ),
        migrations.CreateModel(
            name="MonobankPersonalProvider",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=(
                data_imports.providers.monobank.providers.MonobankProviderBaseMixin,
                "data_imports.provider",
            ),
        ),
    ]
