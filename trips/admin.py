from django.contrib import admin

from .models import Trip, TripParticipant


class TripParticipantInline(admin.TabularInline):
    model = TripParticipant
    extra = 1


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("name", "destination", "start_date", "end_date", "budget", "created_by")
    list_filter = ("destination", "state")
    search_fields = ("name", "destination", "description")
    inlines = [TripParticipantInline]


@admin.register(TripParticipant)
class TripParticipantAdmin(admin.ModelAdmin):
    list_display = ("name", "trip", "user")
