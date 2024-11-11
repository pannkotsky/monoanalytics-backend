from django.db import models

from profiles.models import Account


class StatementImport(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        FINISHED = "finished"
        FAILED = "failed"

    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="statement_imports"
    )
    status = models.CharField(
        max_length=255, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    imported_items_count = models.IntegerField(default=0)
    error = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.account} - {self.created_at}"
