from django.db import models
from ..utils import getModelFields


class User(models.Model):
    userId = models.CharField(primary_key=True, max_length=15)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=30)
    phone_no = models.CharField(max_length=10)
    points = models.IntegerField(default=0)

    def __str__(self):
        return getModelFields(self)


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


# Should this be a base model or relation?
class Friends(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    # friends = models.

    def __str__(self):
        return getModelFields(self)


class Image(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    locationId = models.ForeignKey(Location, on_delete=models.CASCADE)
    description = models.TextField()
    imageURL = models.URLField()
    likes = models.IntegerField(default=0)

    def __str__(self):
        return getModelFields(self)
