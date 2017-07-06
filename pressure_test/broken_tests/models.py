from django.db import models
import os
from config.models import ProjectSetting


# Create your models here.
class CameraProfile(models.Model):
    host = models.CharField(max_length=100)
    user = models.CharField(max_length=100, null=True, blank=True, default='root')
    password = models.CharField(max_length=100, null=True, blank=True)
    project_profile = models.ForeignKey(ProjectSetting, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def get_project_profile_id(self):
        return self.project_profile.id

    class Meta:
        ordering = ('id',)


class NasProfile(models.Model):
    user = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    location = models.TextField()
    workgroup = models.CharField(max_length=100, null=True, blank=True, default='vivotek')
    project_profile = models.ForeignKey(ProjectSetting, on_delete=models.CASCADE, null=True, blank=True)
    
    @property
    def get_project_profile_id(self):
        return self.project_profile.id

    class Meta:
        ordering = ('id',)


class ClipInfo(models.Model):
    full_path = models.TextField()
    size = models.CharField(max_length=100, null=True, blank=True)
    privacy_masks = models.TextField()
    camera_profile = models.ForeignKey(CameraProfile, related_name='camera_profile', on_delete=models.CASCADE, null=True, blank=True)
    nas_profile = models.ForeignKey(NasProfile, related_name='nas_profile', on_delete=models.CASCADE, null=True, blank=True)
    is_broken = models.NullBooleanField(null=True, blank=True)
    creation_time = models.DateTimeField(null=True, blank=True)

    @property
    def get_project_profile_id(self):
        return self.camera_profile.project_profile.id
        
    @property
    def path(self):
        if self.camera_profile.project_profile.type == 'medium':
            return os.path.basename(self.full_path)
        else: 
            return self.full_path.replace(self.nas_profile.location, '')

    @property
    def result(self):
        if self.is_broken == None:
            return "processing"
        elif self.is_broken == False:
            return "passed"
        else:
            return "failed"

    @property
    def errorCode(self):
        is_empty_frame = lambda: self.is_broken and len(list(self.broken_frames.values())) == 0
        has_broken_frame = lambda: self.is_broken and len(list(self.broken_frames.values())) > 0
        MSG_ERR_EMPTY_VIDEO_FRAME = 'empty frame'
        MSG_ERR_BROKEN_VIDEO_FRAME = 'broken frame'
        MSG_NONE = ''
        get_empty_video_frame_err_msg = lambda: MSG_ERR_EMPTY_VIDEO_FRAME
        get_broken_video_frame_err_msg = lambda: MSG_ERR_BROKEN_VIDEO_FRAME
        get_none_msg = lambda: MSG_NONE

        return (is_empty_frame() and get_empty_video_frame_err_msg()) or \
            (has_broken_frame() and get_broken_video_frame_err_msg()) or \
            (not has_broken_frame() and get_none_msg())


    @property
    def count(self):
        """
        broken_frames_count

        """
        return len(list(self.broken_frames.values()))
    
    @property
    def link(self):
        """
        broken_frames_directory

        """
        # assume each directory is the same
        if self.count > 0:
            remote_frame_folder = os.path.join(os.path.dirname(self.full_path), 'broken', os.path.splitext(os.path.basename(self.full_path))[0])
            link_over_web = "ftp://{user}:{password}@{remote_path}".format(
                user= self.nas_profile.user,
                password= self.nas_profile.password,
                remote_path=remote_frame_folder
            )
            return link_over_web
        else:
            return ""
        # if self.count > 0:
        #     first_broken_frame = self.broken_frames.values()[0]
        #     local_frame_folder = os.path.dirname(first_broken_frame['frame_path'])
        #     return local_frame_folder
        # else:
        #     return ""
    
    class Meta:
        ordering = ('id',)


class BrokenFrame(models.Model):
    error_message = models.TextField(null=True, blank=True)
    frame_path = models.TextField()
    timestamp = models.DurationField(null=True, blank=True)
    clip = models.ForeignKey(ClipInfo, related_name='broken_frames', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ('id',)
