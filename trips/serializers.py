from rest_framework import serializers

from .models import Trip, TripParticipant


class TripParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripParticipant
        fields = ["id", "trip", "name", "user"]
        read_only_fields = ["trip"]


class TripSerializer(serializers.ModelSerializer):
    participants = TripParticipantSerializer(many=True, read_only=True)
    status = serializers.ReadOnlyField()
    total_expense = serializers.ReadOnlyField()
    is_over_budget = serializers.ReadOnlyField()
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
            "status",
            "total_expense",
            "is_over_budget",
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
        ]

    def create(self, validated_data):
        names = validated_data.pop("participant_names", [])
        trip = Trip.objects.create(**validated_data)
        for name in names:
            name = name.strip()
            if name:
                TripParticipant.objects.get_or_create(trip=trip, name=name)
        return trip
