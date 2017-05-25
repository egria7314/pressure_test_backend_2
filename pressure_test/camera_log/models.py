from django.db import models

# Create your models here.
class SdStatus(models.Model):
    sd_used_percent = models.FloatField(null=True, blank=True)
    sd_status = models.CharField(null=True, blank=True, max_length=100)
