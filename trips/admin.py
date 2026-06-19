from django.contrib import admin

from .models import CategoryBudget, Hotel, ItineraryDay, Trip, TripParticipant


class TripParticipantInline(admin.TabularInline):
    model = TripParticipant
    extra = 1


class CategoryBudgetInline(admin.TabularInline):
    model = CategoryBudget
    extra = 1


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("name", "destination", "start_date", "end_date", "budget", "created_by")
    list_filter = ("destination", "state")
    search_fields = ("name", "destination", "description")
    inlines = [TripParticipantInline, CategoryBudgetInline]


@admin.register(TripParticipant)
class TripParticipantAdmin(admin.ModelAdmin):
    list_display = ("name", "trip", "user")


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "trip", "check_in_date", "check_out_date", "meal_plan", "booking_status")
    list_filter = ("booking_status", "meal_plan")
    search_fields = ("name", "location")


@admin.register(ItineraryDay)
class ItineraryDayAdmin(admin.ModelAdmin):
    list_display = ("trip", "date", "event", "hotel")
    list_filter = ("trip",)


@admin.register(CategoryBudget)
class CategoryBudgetAdmin(admin.ModelAdmin):
    list_display = ("trip", "category", "allocated_amount")
