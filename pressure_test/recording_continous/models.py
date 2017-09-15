from django.db import models

# Create your models here.
class RecordingContinuty(models.Model):
    project_id = models.CharField(default='-',null=True, blank=True, max_length=100)
    creat_at = models.CharField(null=True, blank=True, max_length=100)
    video_path = models.CharField(null=True, blank=True, max_length=100)
    video_path_before = models.CharField(null=True, blank=True, max_length=100)
    size = models.CharField(null=True, blank=True, max_length=100)
    in_result = models.CharField(null=True, blank=True, max_length=100)
    error_code = models.CharField(null=True, blank=True, max_length=100)
    start_time = models.CharField(null=True, blank=True, max_length=100)
    end_time = models.CharField(null=True, blank=True, max_length=100)
    link = models.CharField(null=True, blank=True, max_length=500)
    count = models.CharField(null=True, blank=True, max_length=100)
    between_result = models.CharField(null=True, blank=True, max_length=100)
    seconds = models.CharField(null=True, blank=True, max_length=100)


class RecordingFile(models.Model):
    project_id = models.CharField(null=True, blank=True, max_length=100)
    modify_time = models.CharField(null=True, blank=True, max_length=100)
    size = models.CharField(null=True, blank=True, max_length=100)
    path = models.CharField(null=True, blank=True, max_length=100)
    status = models.BooleanField(default=False, blank=True, max_length=100)


class Config(models.Model):
    project_id = models.CharField(null=True, blank=True, max_length=100)
    start_time = models.CharField(null=True, blank=True, max_length=100)
    end_time = models.CharField(null=True, blank=True, max_length=100)
    delay_time = models.CharField(null=True, blank=True, max_length=100)