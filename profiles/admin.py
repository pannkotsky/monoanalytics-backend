from django.contrib import admin
from django.utils.translation import gettext as _

from admin_auto_filters.filters import AutocompleteFilterFactory

from currencies.utils import format_amount
from .models import Account, Jar, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("mono_id", "user", "name")
    search_fields = ("name",)
    autocomplete_fields = ("user",)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "mono_id",
        "profile",
        "type",
        "masked_pan",
        "balance_",
        "credit_limit_",
        "statement_last_updated",
    )
    list_filter = ("type", AutocompleteFilterFactory(_("Profile"), "profile"))
    search_fields = ("masked_pan",)
    autocomplete_fields = ("profile",)

    def balance_(self, obj: Account):
        return format_amount(obj.balance, obj.currency_code)

    def credit_limit_(self, obj: Account):
        return format_amount(obj.credit_limit, obj.currency_code)


@admin.register(Jar)
class JarAdmin(admin.ModelAdmin):
    list_display = ("mono_id", "profile", "title", "balance_", "goal_")
    list_filter = (AutocompleteFilterFactory(_("Profile"), "profile"),)
    search_fields = ("title", "description")
    autocomplete_fields = ("profile",)

    def balance_(self, obj: Jar):
        return format_amount(obj.balance, obj.currency_code)

    def goal_(self, obj: Jar):
        return format_amount(obj.goal, obj.currency_code) if obj.goal else None
