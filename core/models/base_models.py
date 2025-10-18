from django.db import models
from django.db.models import Q
from django.utils import timezone
from ..utils import getModelFields


class User(models.Model):
    userId = models.CharField(primary_key=True, max_length=15)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=30)
    phone_no = models.CharField(max_length=10)
    points = models.IntegerField(default=0)

    visited_locations = models.ManyToManyField(
        'Location',
        through='Visit',
        related_name='visitors'
    )

    # This should keep things simpler for now, it'll query every time but if it was a model there'd be redundant data
    # We can't just delete requests if we ever want to celebrate friendship aniversaries or use them for anything else
    def friends(self):
        sent = FriendRequest.objects.filter(from_user=self, status=FriendRequestStatus.ACCEPTED)
        received = FriendRequest.objects.filter(to_user=self, status=FriendRequestStatus.ACCEPTED)
        return User.objects.filter(
            Q(pk__in=sent.values('to_user')) | Q(pk__in=received.values('from_user'))
        )

        # sent = FriendRequest.objects.filter(from_user=self, status="accepted").values_list("to_user", flat=True)
        # received = FriendRequest.objects.filter(to_user=self, status="accepted").values_list("from_user", flat=True)
        # return User.objects.filter(models.Q(pk__in=sent) | models.Q(pk__in=received))

    def add_friend(self, friend):
        self.friends.add(friend)
        friend.friends.add(self)

    def remove_friend(self, other):
        FriendRequest.objects.filter(
            Q(from_user=self, to_user=other) | Q(from_user=other, to_user=self),
            status=FriendRequestStatus.ACCEPTED
        ).delete()

    def __str__(self):
        return getModelFields(self)


class FriendRequestStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    ACCEPTED = 'accepted', 'Accepted'
    REJECTED = 'rejected', 'Rejected'


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    status = models.CharField(
        max_length=8, choices=FriendRequestStatus.choices, default=FriendRequestStatus.PENDING)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['from_user', 'to_user'], name='unique_friend_request')
        ]

    def __str__(self):
        return f"{self.from_user.email} → {self.to_user.email} ({self.status})"


class Achievement(models.Model):
    achievementId = models.CharField(primary_key=True, max_length=10)
    description = models.TextField()
    points = models.IntegerField()

    def __str__(self):
        return getModelFields(self)


class Location(models.Model):
    locationId = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=100)
    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)
    description = models.TextField()
    points = models.IntegerField()

    def __str__(self):
        return getModelFields(self)


class Visit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    visited_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'location'], name='unique_user_location_visit')
        ]

    def __str__(self):
        return getModelFields(self)


class Image(models.Model):
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name="images")
    description = models.TextField()
    imageURL = models.URLField()
    likes = models.IntegerField(default=0)

    def __str__(self):
        return getModelFields(self)
