from django.db import models
from ..utils import getModelFields
from .base_models import *


class HasVisited(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return getModelFields(self)
