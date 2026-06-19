from rest_framework import serializers

from core.categories import EXPENSE_CATEGORY_MAP

from .models import CategoryBudget, Hotel, ItineraryDay, Trip, TripParticipant


class TripParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripParticipant
        fields = ["id", "trip", "name", "user"]


class HotelSerializer(serializers.ModelSerializer):
    amount_paid = serializers.ReadOnlyField()

    class Meta:
        model = Hotel
        fields = [
            "id",
            "trip",
            "name",
            "location",
            "check_in_date",
            "check_out_date",
            "meal_plan",
            "booking_status",
            "notes",
            "amount_paid",
            "created_at",
            "updated_at",
        ]


class ItineraryDaySerializer(serializers.ModelSerializer):
    hotel_name = serializers.ReadOnlyField(source="hotel.name", default=None)
    day_name = serializers.ReadOnlyField()

    class Meta:
        model = ItineraryDay
        fields = [
            "id",
            "trip",
            "date",
            "day_name",
            "event",
            "hotel",
            "hotel_name",
            "notes",
            "order",
        ]


class CategoryBudgetSerializer(serializers.ModelSerializer):
    category_display = serializers.SerializerMethodField()
    spent_amount = serializers.SerializerMethodField()

    class Meta:
        model = CategoryBudget
        fields = ["id", "trip", "category", "category_display", "allocated_amount", "spent_amount"]

    def get_category_display(self, obj):
        return EXPENSE_CATEGORY_MAP.get(obj.category, obj.category)

    def get_spent_amount(self, obj):
        from django.db.models import Sum

        return obj.trip.expenses.filter(category=obj.category).aggregate(total=Sum("amount"))[
            "total"
        ] or 0


class TripSerializer(serializers.ModelSerializer):
    participants = TripParticipantSerializer(many=True, read_only=True)
    category_budgets = CategoryBudgetSerializer(many=True, read_only=True)
    status = serializers.ReadOnlyField()
    total_expense = serializers.ReadOnlyField()
    is_over_budget = serializers.ReadOnlyField()
    balance = serializers.ReadOnlyField()
    created_by_name = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = Trip
        fields = [
            "id",
            "name",
            "description",
            "destination",
            "state",
            "start_date",
            "end_date",
            "budget",
            "default_split_type",
            "participants",
            "category_budgets",
            "status",
            "total_expense",
            "is_over_budget",
            "balance",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by"]


class TripCreateSerializer(serializers.ModelSerializer):
    participant_names = serializers.ListField(
        child=serializers.CharField(max_length=150), write_only=True, required=False
    )
    category_budgets = serializers.DictField(
        child=serializers.DecimalField(max_digits=12, decimal_places=2),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Trip
        fields = [
            "id",
            "name",
            "description",
            "destination",
            "state",
            "start_date",
            "end_date",
            "budget",
            "default_split_type",
            "participant_names",
            "category_budgets",
        ]

    def create(self, validated_data):
        names = validated_data.pop("participant_names", [])
        budgets = validated_data.pop("category_budgets", {})
        trip = Trip.objects.create(**validated_data)
        for name in names:
            name = name.strip()
            if name:
                TripParticipant.objects.get_or_create(trip=trip, name=name)
        for category, amount in budgets.items():
            if category in EXPENSE_CATEGORY_MAP and amount:
                CategoryBudget.objects.get_or_create(
                    trip=trip, category=category, defaults={"allocated_amount": amount}
                )
        return trip
