from django.urls import path

from . import pages

app_name = "trips"

urlpatterns = [
    path("", pages.home, name="home"),
    path("trips/new/", pages.trip_form, name="trip_create"),
    path("trips/<int:pk>/edit/", pages.trip_form, name="trip_edit"),
    path("trips/<int:pk>/", pages.trip_detail, name="trip_detail"),
]
