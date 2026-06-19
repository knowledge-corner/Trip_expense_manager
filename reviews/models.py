from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from trips.models import Hotel, Trip


class PlaceReview(models.Model):
    PLACE_TYPE_CHOICES = [
        ("restaurant", "Restaurant"),
        ("hotel", "Hotel"),
        ("attraction", "Attraction"),
        ("other", "Other"),
    ]

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="reviews")
    place_name = models.CharField(max_length=200)
    place_type = models.CharField(
        max_length=20, choices=PLACE_TYPE_CHOICES, default="restaurant"
    )
    location = models.CharField(max_length=200, blank=True)
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviews",
        help_text="Link this review to a hotel booking, if applicable.",
    )
    rating = models.PositiveSmallIntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    amount_spent = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    review_text = models.TextField(blank=True)
    would_revisit = models.BooleanField(default=True)
    alternative_suggestion = models.CharField(
        max_length=255,
        blank=True,
        help_text="A better alternative found nearby, if any",
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.place_name} ({self.trip.name})"
