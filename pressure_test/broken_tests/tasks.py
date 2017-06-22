from __future__ import absolute_import
from celery import shared_task
from broken_tests.models import ClipInfo, CameraProfile, NasProfile
from broken_tests.helpers.roi_module import RoiModule
from libs.nas_storage import NasStorage
from libs.vast_storage import VastStorage

import os


# @shared_task
# def outer(param):
#     return 'The test task executed with argument "%s" ' % param


def arrange_periodic_task(camera_id, nas_id, start_time, end_time):
    print( "camera_id: ", camera_id, "nas_id: ", nas_id )
    camera = CameraProfile.objects.get(id=camera_id)
    nas = NasProfile.objects.get(id=nas_id)
    remote_batch_clips = []
    print( "type: ", "'{}'".format(nas.project_profile.type))
    if nas.project_profile.type == 'high':
        nas_helper = NasStorage(nas.user, nas.password)
        remote_batch_clips = nas_helper.get_video_nas(nas.user, nas.password, '', nas.location, camera.project_profile.prefix_name, start_time, end_time)
        print("NAS batch clips: ", remote_batch_clips)
    elif nas.project_profile.type == 'medium':
        vast_helper = VastStorage(nas.user, nas.password)
        print("Mount and Get vast file")
        remote_batch_clips = vast_helper.get_video_vast(nas.user, nas.password, '', nas.location, start_time, end_time)
        print("VAST batch clips: ", remote_batch_clips)
    # unhandled_clips = ["//172.19.11.191/eric/alphago/20170615/20/medium_stress04.mp4", "//172.19.11.191/eric/alphago/20170615/20/medium_stress05.mp4", "//172.19.11.191/eric/alphago/20170615/20/medium_stress06.mp4"]
    print( "got unhandle files: ", remote_batch_clips )
        

    for file_path in remote_batch_clips:
        camera = CameraProfile.objects.get(id=camera_id)
        print( "got camera: ", camera.id )
        nas = NasProfile.objects.get(id=nas_id)
        print( "got nas: ", nas.id )
        video_destination = 'VAST' if nas.project_profile.type == 'medium' else 'NAS'
        roi = RoiModule(camera.host, camera.user, camera.password, video_destination)
        clip, created = ClipInfo.objects.get_or_create(full_path=file_path)
        if created or clip.is_broken == None:
            clip.privacy_masks = str(roi.return_mask())
            clip.camera_profile = camera
            clip.nas_profile = nas
            clip.save()
            print( "got clip: ", clip.id )
            push_detect_broken_image_tasks_to_queue.apply_async(args=[clip.id], queue='broken_test_camera{}'.format(camera.id))
            print( 'push finished: ', clip.id )


@shared_task
def push_detect_broken_image_tasks_to_queue(clip_id):
    from broken_tests import views
    print("PUSH QUEUE:", clip_id)
    views.detect_broken_image(clip_id)
    

@shared_task
def check_single_image_as_usual(privacy_masks, image_path):
    from broken_tests.helpers.content_analysis import ContentAnalysis
    print("IMAGE PATH:", image_path)
    params = (privacy_masks, image_path)
    return ContentAnalysis().check_single_image_as_usual(params)