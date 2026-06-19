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

    @property
    def balance(self):
        if self.budget is None:
            return None
        return self.budget - self.total_expense


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


class Hotel(models.Model):
    MEAL_NONE = "none"
    MEAL_BREAKFAST = "breakfast"
    MEAL_BREAKFAST_DINNER = "breakfast_dinner"
    MEAL_ALL = "all_meals"
    MEAL_PLAN_CHOICES = [
        (MEAL_NONE, "No meals included"),
        (MEAL_BREAKFAST, "Breakfast included"),
        (MEAL_BREAKFAST_DINNER, "Breakfast & Dinner included"),
        (MEAL_ALL, "All meals included"),
    ]
    STATUS_PLANNED = "planned"
    STATUS_BOOKED = "booked"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    BOOKING_STATUS_CHOICES = [
        (STATUS_PLANNED, "Planned (not booked)"),
        (STATUS_BOOKED, "Booked"),
        (STATUS_COMPLETED, "Stay completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="hotels")
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    check_in_date = models.DateField(null=True, blank=True)
    check_out_date = models.DateField(null=True, blank=True)
    meal_plan = models.CharField(max_length=20, choices=MEAL_PLAN_CHOICES, default=MEAL_NONE)
    booking_status = models.CharField(
        max_length=20, choices=BOOKING_STATUS_CHOICES, default=STATUS_PLANNED
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["check_in_date", "name"]

    def __str__(self):
        return f"{self.name} ({self.trip.name})"

    @property
    def amount_paid(self):
        from django.db.models import Sum

        return self.expenses.aggregate(total=Sum("amount"))["total"] or 0


class ItineraryDay(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="itinerary_days")
    date = models.DateField()
    event = models.CharField(max_length=255, blank=True)
    hotel = models.ForeignKey(
        Hotel, on_delete=models.SET_NULL, null=True, blank=True, related_name="itinerary_days"
    )
    notes = models.TextField(blank=True, help_text="Free-form day plan / things to do")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["date", "order", "id"]

    def __str__(self):
        return f"{self.date} - {self.event or 'Day plan'} ({self.trip.name})"

    @property
    def day_name(self):
        return self.date.strftime("%A")


class CategoryBudget(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="category_budgets")
    category = models.CharField(max_length=30)
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("trip", "category")
        ordering = ["category"]

    def __str__(self):
        return f"{self.category}: {self.allocated_amount} ({self.trip.name})"
