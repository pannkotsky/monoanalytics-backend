# Generated by Django 4.2.16 on 2024-09-09 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("statement", "0002_alter_merchantcategory_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="merchantcategory",
            name="description_ua",
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name="merchantcategory",
            name="description",
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name="statementitem",
            name="counter_name",
            field=models.CharField(blank=True, max_length=256),
        ),
    ]