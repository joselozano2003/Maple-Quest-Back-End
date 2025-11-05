from django.contrib import admin
from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "email", "phone_no", "points")
    search_fields = ("user_id", "email")


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("achievement_id", "description", "points")
    search_fields = ("achievement_id", "description")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("location_id", "name", "latitude", "longitude", "description", "points")
    search_fields = ("location_id", "name", "description")


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ("from_user", "to_user", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("from_user__email", "to_user__email")


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("user", "location", "visited_at", "note")
    list_filter = ("visited_at",)
    search_fields = ("user__email", "location__name", "note")


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("visit", "description", "image_url", "likes")
    search_fields = ("visit__user__email", "visit__location__name", "description")
