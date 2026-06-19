from decimal import Decimal

from rest_framework import serializers

from trips.models import TripParticipant

from .models import Expense, ExpenseSplit


class ExpenseSplitSerializer(serializers.ModelSerializer):
    participant_name = serializers.ReadOnlyField(source="participant.name")

    class Meta:
        model = ExpenseSplit
        fields = ["id", "participant", "participant_name", "amount"]


class ExpenseSerializer(serializers.ModelSerializer):
    splits = ExpenseSplitSerializer(many=True, required=False)
    category_display = serializers.ReadOnlyField(source="get_category_display")
    paid_by_name = serializers.ReadOnlyField(source="paid_by.name", default=None)
    hotel_name = serializers.ReadOnlyField(source="hotel.name", default=None)
    created_by_name = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = Expense
        fields = [
            "id",
            "trip",
            "category",
            "category_display",
            "amount",
            "date",
            "description",
            "location",
            "hotel",
            "hotel_name",
            "paid_by",
            "paid_by_name",
            "split_type",
            "splits",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by"]

    def validate(self, attrs):
        split_type = attrs.get("split_type", getattr(self.instance, "split_type", Expense.SPLIT_SINGLE))
        splits = attrs.get("splits")
        if split_type == Expense.SPLIT_CUSTOM:
            if not splits:
                raise serializers.ValidationError(
                    {"splits": "Custom split requires at least one participant share."}
                )
            amount = attrs.get("amount", getattr(self.instance, "amount", None))
            total = sum(Decimal(str(s["amount"])) for s in splits)
            if amount is not None and total != Decimal(str(amount)):
                raise serializers.ValidationError(
                    {"splits": f"Split amounts ({total}) must add up to the expense amount ({amount})."}
                )
        return attrs

    def _apply_splits(self, expense, split_type, splits_data):
        expense.splits.all().delete()
        if split_type == Expense.SPLIT_EQUAL:
            participants = list(expense.trip.participants.all())
            if participants:
                share = (expense.amount / len(participants)).quantize(Decimal("0.01"))
                remainder = expense.amount - (share * len(participants))
                for idx, participant in enumerate(participants):
                    amt = share + remainder if idx == 0 else share
                    ExpenseSplit.objects.create(expense=expense, participant=participant, amount=amt)
        elif split_type == Expense.SPLIT_CUSTOM and splits_data:
            for split in splits_data:
                ExpenseSplit.objects.create(
                    expense=expense, participant=split["participant"], amount=split["amount"]
                )

    def create(self, validated_data):
        splits_data = validated_data.pop("splits", [])
        expense = Expense.objects.create(**validated_data)
        self._apply_splits(expense, expense.split_type, splits_data)
        return expense

    def update(self, instance, validated_data):
        splits_data = validated_data.pop("splits", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self._apply_splits(instance, instance.split_type, splits_data or [])
        return instance
