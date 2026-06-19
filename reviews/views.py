from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from .models import PlaceReview
from .serializers import PlaceReviewSerializer


class IsOwnerOrReadOnlyForOthers(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by_id == request.user.id or request.user.is_staff


class PlaceReviewViewSet(viewsets.ModelViewSet):
    queryset = PlaceReview.objects.select_related("trip", "created_by")
    serializer_class = PlaceReviewSerializer
    permission_classes = [IsOwnerOrReadOnlyForOthers]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["trip", "place_type", "rating"]
    search_fields = ["place_name", "location", "review_text"]
    ordering_fields = ["created_at", "rating", "amount_spent"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
