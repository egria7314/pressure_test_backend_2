from config.models import ProjectSetting
from django.db.models.signals import post_save
from django.dispatch import receiver

from broken_tests.models import CameraProfile, NasProfile
import os


@receiver(post_save, sender=ProjectSetting)
def save_camera_and_nas_profile(sender, instance, **kwargs):
    """
    """
    # Now Project and Camera object is 1:1
    camera, created = CameraProfile.objects.get_or_create(project_profile=instance)
    camera.host = instance.ip
    camera.user = instance.username
    camera.password = instance.password
    camera.save()

    # Now Project and Nas object is 1:1
    nas, created = NasProfile.objects.get_or_create(project_profile=instance)
    nas.user = instance.path_username
    nas.password = instance.path_password
    nas.location = os.path.join(instance.path, '') # ensure location with ending slash
    nas.save()