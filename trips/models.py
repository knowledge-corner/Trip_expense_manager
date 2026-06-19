from django.conf import settings
from django.db import models
from django.utils import timezone


class Trip(models.Model):
    SPLIT_SINGLE = "single"
    SPLIT_EQUAL = "equal"
    SPLIT_TYPE_CHOICES = [
        (SPLIT_SINGLE, "Single Payer (no split)"),
        (SPLIT_EQUAL, "Split Among Participants"),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    destination = models.CharField(max_length=200)
    state = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    default_split_type = models.CharField(
        max_length=10, choices=SPLIT_TYPE_CHOICES, default=SPLIT_EQUAL
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trips"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.name

    @property
    def status(self):
        today = timezone.localdate()
        if self.start_date > today:
            return "upcoming"
        if self.end_date:
            return "completed" if self.end_date < today else "ongoing"
        return "completed" if self.start_date < today else "ongoing"

    @property
    def total_expense(self):
        from django.db.models import Sum

        return self.expenses.aggregate(total=Sum("amount"))["total"] or 0

    @property
    def is_over_budget(self):
        return bool(self.budget) and self.total_expense > self.budget


class TripParticipant(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="participants")
    name = models.CharField(max_length=150)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trip_participations",
    )

    class Meta:
        unique_together = ("trip", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.trip.name})"
