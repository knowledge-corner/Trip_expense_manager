from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.categories import EXPENSE_CATEGORY_CHOICES

from .models import Expense
from .serializers import ExpenseSerializer


class IsOwnerOrReadOnlyForOthers(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by_id == request.user.id or request.user.is_staff


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.select_related("trip", "paid_by", "created_by").prefetch_related("splits")
    serializer_class = ExpenseSerializer
    permission_classes = [IsOwnerOrReadOnlyForOthers]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["trip", "category", "split_type", "paid_by"]
    search_fields = ["description", "location"]
    ordering_fields = ["date", "amount", "created_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["get"])
    def categories(self, request):
        return Response([{"value": v, "label": l} for v, l in EXPENSE_CATEGORY_CHOICES])
