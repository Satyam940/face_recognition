from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# models.py
from django.db import models

class KnownFace(models.Model):
    name = models.CharField(max_length=100)
    uid = models.CharField(max_length=100, unique=True)
    class_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='known_faces/', null=True, blank=True)
    encoding = models.TextField()
    password = models.CharField(max_length=255)  # Added password field

    def __str__(self):
        return self.name




class Attendance(models.Model):
    student = models.ForeignKey(KnownFace, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    date_time = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=False)  # True = Present, False = Absent

    def __str__(self):
        return f"{self.student.name} - {self.subject} - {'Present' if self.status else 'Absent'}"