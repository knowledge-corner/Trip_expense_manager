from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Trip


@login_required
def home(request):
    return render(request, "trips/home.html")


@login_required
def trip_form(request, pk=None):
    trip = get_object_or_404(Trip, pk=pk) if pk else None
    return render(request, "trips/trip_form.html", {"trip": trip, "trip_id": pk})


@login_required
def trip_detail(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    return render(request, "trips/trip_detail.html", {"trip": trip})
