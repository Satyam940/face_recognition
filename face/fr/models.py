from django.db import models
import json
import numpy as np 

class KnownFace(models.Model):
    name = models.CharField(max_length=100)
    uid = models.CharField(max_length=100, unique=True)
    class_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='known_faces/', null=True, blank=True)
    encoding = models.TextField()  

    def set_encoding(self, encoding_array):
        self.encoding = json.dumps(encoding_array.tolist())

    def get_encoding(self):
        return np.array(json.loads(self.encoding))

    def __str__(self):
        return f"{self.name}"