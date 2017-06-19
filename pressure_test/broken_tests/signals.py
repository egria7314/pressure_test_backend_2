from config.models import ProjectSetting
from django.db.models.signals import post_save
from django.dispatch import receiver

from broken_tests.models import CameraProfile, NasProfile



@receiver(post_save, sender=ProjectSetting)
def save_camera_and_nas_profile(sender, instance, **kwargs):
    """
    """
    CameraProfile.objects.create(
        host=instance.ip,
        user=instance.username,
        password=instance.password,
        project_profile=instance
    )

    NasProfile.objects.create(
        user=instance.path_username,
        password=instance.path_password,
        location=instance.path,
        project_profile=instance
    )

