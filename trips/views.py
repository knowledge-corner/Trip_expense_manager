from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.categories import EXPENSE_CATEGORY_MAP
from expenses.models import Expense

from .models import CategoryBudget, Hotel, ItineraryDay, Trip, TripParticipant
from .serializers import (
    CategoryBudgetSerializer,
    HotelSerializer,
    ItineraryDaySerializer,
    TripCreateSerializer,
    TripParticipantSerializer,
    TripSerializer,
)


class IsOwnerOrReadOnlyForOthers(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by_id == request.user.id or request.user.is_staff


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.select_related("created_by").prefetch_related(
        "participants", "category_budgets"
    ).all()
    permission_classes = [IsOwnerOrReadOnlyForOthers]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["destination", "state"]
    search_fields = ["name", "destination", "description", "state"]
    ordering_fields = ["start_date", "end_date", "budget", "created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return TripCreateSerializer
        return TripSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        year = self.request.query_params.get("year")
        if year:
            qs = qs.filter(start_date__year=year)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            ids = [trip.id for trip in qs if trip.status == status_filter]
            qs = qs.filter(id__in=ids)
        return qs

    def perform_create(self, serializer):
        trip = serializer.save(created_by=self.request.user)
        if not trip.participants.exists():
            TripParticipant.objects.create(trip=trip, name=self.request.user.get_full_name() or self.request.user.username, user=self.request.user)

    @action(detail=True, methods=["get"])
    def analytics(self, request, pk=None):
        trip = self.get_object()
        category_totals = {
            row["category"]: row["total"]
            for row in trip.expenses.values("category").annotate(total=Sum("amount"))
        }
        all_categories = set(category_totals) | set(
            trip.category_budgets.values_list("category", flat=True)
        )
        budgets = {cb.category: cb.allocated_amount for cb in trip.category_budgets.all()}
        category_data = [
            {
                "category": cat,
                "category_display": EXPENSE_CATEGORY_MAP.get(cat, cat),
                "total": category_totals.get(cat, 0),
                "budget": budgets.get(cat),
            }
            for cat in sorted(all_categories, key=lambda c: -float(category_totals.get(c, 0)))
        ]
        daily_totals = (
            trip.expenses.values("date").annotate(total=Sum("amount")).order_by("date")
        )
        participant_paid = (
            trip.expenses.exclude(paid_by__isnull=True)
            .values("paid_by__id", "paid_by__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )
        return Response(
            {
                "trip_id": trip.id,
                "total_expense": trip.total_expense,
                "budget": trip.budget,
                "balance": trip.balance,
                "is_over_budget": trip.is_over_budget,
                "by_category": category_data,
                "by_date": list(daily_totals),
                "by_participant": list(participant_paid),
            }
        )

    @action(detail=False, methods=["get"])
    def filters_meta(self, request):
        years = sorted(
            {t.start_date.year for t in Trip.objects.all()}, reverse=True
        )
        states = sorted({t.state for t in Trip.objects.exclude(state="") })
        destinations = sorted({t.destination for t in Trip.objects.exclude(destination="")})
        return Response({"years": years, "states": states, "destinations": destinations})


class TripParticipantViewSet(viewsets.ModelViewSet):
    queryset = TripParticipant.objects.all()
    serializer_class = TripParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["trip"]


class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.select_related("trip").all()
    serializer_class = HotelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["trip", "booking_status"]


class ItineraryDayViewSet(viewsets.ModelViewSet):
    queryset = ItineraryDay.objects.select_related("trip", "hotel").all()
    serializer_class = ItineraryDaySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["trip"]


class CategoryBudgetViewSet(viewsets.ModelViewSet):
    queryset = CategoryBudget.objects.select_related("trip").all()
    serializer_class = CategoryBudgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["trip"]
