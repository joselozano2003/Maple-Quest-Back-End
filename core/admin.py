from django.contrib import admin
from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("userId", "email", "phone_no", "points")
    search_fields = ("userId", "email")


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("achievementId", "description", "points")
    search_fields = ("achievementId", "description")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("locationId", "name", "latitude", "longitude", "description", "points")
    search_fields = ("locationId", "name", "description")


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("userId", "locationId", "description", "imageURL", "likes")
    search_fields = ("userId", "locationId", "description")
