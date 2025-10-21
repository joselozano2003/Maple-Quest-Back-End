from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'friend-requests', FriendRequestViewSet, basename='friendrequest')
router.register(r'users', UserViewSet, basename='user')
router.register(r'achievements', AchievementViewSet, basename='achievement')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'visits', VisitViewSet, basename='visit')
router.register(r'images', ImageViewSet, basename='image')

urlpatterns = [
    path('', include(router.urls))
]
