from django.contrib import admin

from .models import PlaceReview


@admin.register(PlaceReview)
class PlaceReviewAdmin(admin.ModelAdmin):
    list_display = ("place_name", "trip", "place_type", "rating", "amount_spent")
    list_filter = ("place_type", "rating")
    search_fields = ("place_name", "location", "review_text")
