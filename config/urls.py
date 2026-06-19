from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from expenses.views import ExpenseViewSet
from reviews.views import PlaceReviewViewSet
from trips.views import (
    CategoryBudgetViewSet,
    HotelViewSet,
    ItineraryDayViewSet,
    TripParticipantViewSet,
    TripViewSet,
)

router = DefaultRouter()
router.register("trips", TripViewSet, basename="trip")
router.register("participants", TripParticipantViewSet, basename="participant")
router.register("hotels", HotelViewSet, basename="hotel")
router.register("itinerary-days", ItineraryDayViewSet, basename="itineraryday")
router.register("category-budgets", CategoryBudgetViewSet, basename="categorybudget")
router.register("expenses", ExpenseViewSet, basename="expense")
router.register("reviews", PlaceReviewViewSet, basename="review")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path("accounts/", include("accounts.urls")),
    path("backup/", include("core.urls")),
    path("", include("trips.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
