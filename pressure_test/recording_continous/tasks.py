from __future__ import absolute_import
from celery import shared_task

#TODO:change to carlos
# rom clips.helpers.content_analysis import ContentAnalysis
# from clips import views
import os
# from clips.helpers.roi_module import RoiModule
# from clips.models import ClipInfo, CameraProfile, NasProfile
import datetime, time
from config.models import ProjectSetting
from libs.nas_storage import NasStorage

from recording_continous.models import RecordingContinuty
from recording_continous.models import RecordingFile
from recording_continous.models import Config
from recording_continous.video_continous import VideoContinous

def arrange_periodic_task(project_id, start_time, end_time):
    ns = NasStorage()
    obj = ProjectSetting.objects.get(id=project_id)
    remote_path = obj.path
    remote_username = obj.path_username
    remote_password = obj.path_password
    sudo_password = ""
    prefix = obj.prefix_name

    clips = ns.get_video_nas(remote_username, remote_password, sudo_password, remote_path, prefix, start_time, end_time)

    for file_path in sorted(clips):
        push_detect_broken_image_tasks_to_queue(remote_username, remote_password, project_id, remote_path, file_path)
        time.sleep(5)

    # for file_path in clips:
    #     push_detect_broken_image_tasks_to_queue.apply_async(args=[remote_username, remote_password, project_id, remote_path, file_path],queue='continous_test_camera{}'.format(str(project_id)))
    #     time.sleep(5)

def push_detect_broken_image_tasks_to_queue(remote_username, remote_password, project_id, remote_path, file_path):
    from libs.nas_storage import NasStorage
    from recording_continous.models import Config
    from recording_continous.video_continous import VideoContinous
    from recording_continous.models import RecordingFile
    import os

    local_path = os.path.join("/mnt/", remote_path.replace('//', '').replace('/', '_'))
    clippath = os.path.join(local_path, file_path.lower()[len(remote_path) + 1:])
    ns = NasStorage()
    ns.mount_folder(remote_username, remote_password, remote_path, '', local_path)
    query = RecordingFile.objects.filter(project_id=project_id).order_by('-id')[0]
    file_path_before = query.path


    file_modify_time =  datetime.datetime.fromtimestamp(os.stat(clippath).st_mtime)
    file_size = str(int(os.path.getsize(clippath)/1000000))+' MB'
    RecordingFile.objects.create(
        project_id=project_id,
        modify_time=str(file_modify_time),
        size = file_size,
        path = clippath,

    )
    print("PUSH QUEUE:", clippath)
    vc = VideoContinous(file_path_before, clippath)
    in_result = vc.continuity_in_recording_files()
    query = RecordingFile.objects.filter(project_id=project_id)
    if len(query)>0:
        between_result = vc.continuity_bwtween_recording_files()
    else :
        between_result ={}
        between_result["between_result"] = 'failed'
        between_result["seconds"] = 'First video'

    RecordingContinuty.objects.create(
        project_id=project_id,
        creat_at=str(file_modify_time),
        video_path=file_path.replace(remote_path+"/", ""),
        video_path_before=file_path_before.replace(local_path+"/", ""),
        size=file_size,
        in_result=in_result["in_result"],
        error_code=in_result["error_code"],
        start_time=in_result["start_time"],
        end_time=in_result["start_time"],
        link=in_result["link"],
        count=in_result["count"],
        between_result=between_result["between_result"],
        seconds=between_result["seconds"],

        )

# @shared_task
# def push_detect_broken_image_tasks_to_queue(remote_username, remote_password, project_id, remote_path, file_path):
#     from libs.nas_storage import NasStorage
#     from recording_continous.models import Config
#     from recording_continous.video_continous import VideoContinous
#     from recording_continous.models import RecordingFile
#     import os
#
#
#
#     local_path = os.path.join("/mnt/", remote_path.replace('//', '').replace('/', '_'))
#     clippath = os.path.join(local_path, file_path.lower()[len(remote_path) + 1:])
#
#     ns = NasStorage()
#     ns.mount_folder(remote_username, remote_password, remote_path, '', local_path)
#
#     query = RecordingFile.objects.filter(project_id=project_id).order_by('-id')[0]
#
#     file_path_before = query.path
#
#     file_modify_time =  datetime.datetime.fromtimestamp(os.stat(clippath).st_mtime)
#     file_size = str((os.path.getsize(clippath)/1000000))+' MB'
#
#     RecordingFile.objects.create(
#         project_id=project_id,
#         modify_time=str(file_modify_time),
#         size= file_size,
#         path=clippath,
#
#     )
#
#     print("PUSH QUEUE:", clippath)
#
#     vc = VideoContinous(file_path_before, clippath)
#     in_result = vc.continuity_in_recording_files()
#     between_result = vc.continuity_bwtween_recording_files()
#
#     RecordingContinuty.objects.create(
#         project_id=project_id,
#         creat_at=str(file_modify_time),
#         video_path=file_path.replace(remote_path + "/", ""),
#         video_path_before=file_path_before.replace(local_path + "/", ""),
#         size=file_size,
#         in_result=in_result["in_result"],
#         error_code=in_result["error_code"],
#         start_time=in_result["start_time"],
#         end_time=in_result["start_time"],
#         link=in_result["link"],
#         count=in_result["count"],
#         between_result=between_result["between_result"],
#         seconds=between_result["seconds"],
#
#     )
