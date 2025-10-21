from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializers import *


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer

    # detail=True -> the URL includes the pk of the object
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        friend_request: FriendRequest = self.get_object()  # get the object based on the URL's pk
        friend_request.status = FriendRequestStatus.ACCEPTED
        friend_request.save()

        return Response({'status': 'accepted'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        friend_request: FriendRequest = self.get_object()
        friend_request.status = FriendRequestStatus.REJECTED
        friend_request.save()

        return Response({'status': 'rejected'}, status=status.HTTP_200_OK)


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class VisitViewSet(viewsets.ModelViewSet):
    queryset = Visit.objects.all()
    serializer_class = VisitSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
