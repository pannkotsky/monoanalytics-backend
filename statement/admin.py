from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.utils.translation import gettext as _

from admin_auto_filters.filters import AutocompleteFilterMultiple
from rangefilter.filters import DateRangeFilterBuilder

from currencies.utils import CURRENCIES, format_amount
from .models import MerchantCategory, StatementItem, Tag


class AccountAutocompleteFilter(AutocompleteFilterMultiple):
    title = _("Account")
    field_name = "account"


class MerchantCategoryAutocompleteFilter(AutocompleteFilterMultiple):
    title = _("Merchant category")
    field_name = "merchant_category"


class TagAutocompleteFilter(AutocompleteFilterMultiple):
    title = _("Tag")
    field_name = "tags"


class CurrencyFilter(SimpleListFilter):
    title = _("Currency")
    parameter_name = "currency"

    def lookups(self, request, model_admin):
        return [(code, currency["name"]) for code, currency in CURRENCIES.items()]

    def queryset(self, request, queryset):
        if value := self.value():
            return queryset.filter(account__currency_code=value)
        return queryset


@admin.register(MerchantCategory)
class MerchantCategoryAdmin(admin.ModelAdmin):
    list_display = ("code", "description", "description_ua")
    search_fields = ("code", "description", "description_ua")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(StatementItem)
class StatementItemAdmin(admin.ModelAdmin):
    list_display = (
        "account",
        "time",
        "description",
        "merchant_category",
        "amount_in_account_currency_",
        "balance_",
        "tags_",
    )
    list_filter = (
        AccountAutocompleteFilter,
        MerchantCategoryAutocompleteFilter,
        TagAutocompleteFilter,
        ("time", DateRangeFilterBuilder()),
        CurrencyFilter,
    )
    search_fields = ("description", "counter_name")
    autocomplete_fields = ("account", "merchant_category")
    ordering = ("-time",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("account")

    def amount_in_account_currency_(self, obj: StatementItem):
        return format_amount(obj.amount_in_account_currency, obj.account.currency_code)

    def balance_(self, obj: StatementItem):
        return format_amount(obj.balance, obj.account.currency_code)

    def tags_(self, obj: StatementItem):
        return ", ".join([tag.name for tag in obj.tags.all()])
