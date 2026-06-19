from django.contrib import admin

from .models import Expense, ExpenseSplit


class ExpenseSplitInline(admin.TabularInline):
    model = ExpenseSplit
    extra = 1


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("trip", "category", "amount", "date", "paid_by", "split_type")
    list_filter = ("category", "split_type", "trip")
    search_fields = ("description", "location")
    inlines = [ExpenseSplitInline]
