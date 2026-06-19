from rest_framework import serializers

from .models import PlaceReview


class PlaceReviewSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = PlaceReview
        fields = [
            "id",
            "trip",
            "place_name",
            "place_type",
            "location",
            "rating",
            "amount_spent",
            "review_text",
            "would_revisit",
            "alternative_suggestion",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by"]
