from django.db import models

# Create your models here.
class RecordingContinuty(models.Model):
    project_id = models.CharField(default='-',null=True, blank=True, max_length=500)
    creat_at = models.CharField(null=True, blank=True, max_length=500)
    video_path = models.CharField(null=True, blank=True, max_length=500)
    video_path_before = models.CharField(null=True, blank=True, max_length=500)
    size = models.CharField(null=True, blank=True, max_length=500)
    in_result = models.CharField(null=True, blank=True, max_length=500)
    error_code = models.CharField(null=True, blank=True, max_length=500)
    start_time = models.CharField(null=True, blank=True, max_length=500)
    end_time = models.CharField(null=True, blank=True, max_length=500)
    link = models.CharField(null=True, blank=True, max_length=500)
    count = models.CharField(null=True, blank=True, max_length=500)
    between_result = models.CharField(null=True, blank=True, max_length=500)
    seconds = models.CharField(null=True, blank=True, max_length=500)


class RecordingFile(models.Model):
    project_id = models.CharField(null=True, blank=True, max_length=500)
    modify_time = models.CharField(null=True, blank=True, max_length=500)
    size = models.CharField(null=True, blank=True, max_length=500)
    path = models.CharField(null=True, blank=True, max_length=500)
    status = models.BooleanField(default=False, blank=True, max_length=500)


class Config(models.Model):
    project_id = models.CharField(null=True, blank=True, max_length=500)
    start_time = models.CharField(null=True, blank=True, max_length=500)
    end_time = models.CharField(null=True, blank=True, max_length=500)
    delay_time = models.CharField(null=True, blank=True, max_length=500)