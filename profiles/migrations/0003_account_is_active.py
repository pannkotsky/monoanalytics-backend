# Generated by Django 5.1.1 on 2024-11-06 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0002_remove_profile_webhook_url_account_last_updated_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]