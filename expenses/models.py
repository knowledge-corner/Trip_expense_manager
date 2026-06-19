from django.conf import settings
from django.db import models

from core.categories import EXPENSE_CATEGORY_CHOICES
from trips.models import Trip, TripParticipant


class Expense(models.Model):
    SPLIT_SINGLE = "single"
    SPLIT_EQUAL = "equal"
    SPLIT_CUSTOM = "custom"
    SPLIT_TYPE_CHOICES = [
        (SPLIT_SINGLE, "Not split (single payer)"),
        (SPLIT_EQUAL, "Split equally"),
        (SPLIT_CUSTOM, "Custom split"),
    ]

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="expenses")
    category = models.CharField(max_length=30, choices=EXPENSE_CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=200, blank=True)
    paid_by = models.ForeignKey(
        TripParticipant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paid_expenses",
    )
    split_type = models.CharField(
        max_length=10, choices=SPLIT_TYPE_CHOICES, default=SPLIT_SINGLE
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="expenses_logged"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.get_category_display()} - {self.amount} ({self.trip.name})"


class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="splits")
    participant = models.ForeignKey(
        TripParticipant, on_delete=models.CASCADE, related_name="expense_shares"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("expense", "participant")

    def __str__(self):
        return f"{self.participant.name}: {self.amount}"
