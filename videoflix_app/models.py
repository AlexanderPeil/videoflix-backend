from django.db import models
from datetime import date


class Video(models.Model):
    created_at = models.DateField(default=date.today)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    genre = models.CharField(max_length=50)
    video_file = models.FileField(upload_to='videos', blank=True, null=True)
    video_file_480 = models.FileField(upload_to='videos', blank=True, null=True)
    video_file_720 = models.FileField(upload_to='videos', blank=True, null=True)
    video_file_1000 = models.FileField(upload_to='videos', blank=True, null=True)

    def __str__(self):
        return self.title