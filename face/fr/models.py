# models.py
from django.db import models


class KnownFace(models.Model):
    name = models.CharField(max_length=100)
    uid = models.CharField(max_length=100, unique=True)
    class_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='known_faces/', null=True, blank=True)
    encoding = models.TextField()

    def __str__(self):
        return self.name