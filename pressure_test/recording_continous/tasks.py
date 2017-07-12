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
from libs.vast_storage import VastStorage

from recording_continous.models import RecordingContinuty
from recording_continous.models import RecordingFile
from recording_continous.models import Config
from recording_continous.video_continous import VideoContinous
from libs.pressure_test_logging import PressureTestLogging as ptl


def arrange_periodic_task(project_id, start_time, end_time):
    obj = ProjectSetting.objects.get(id=project_id)
    remote_path = obj.path
    remote_username = obj.path_username
    remote_password = obj.path_password
    sudo_password = ""
    prefix = obj.prefix_name
    pressure_test_video_type = obj.type
    delay_time = obj.delay

    if pressure_test_video_type == 'medium':
        vast = VastStorage()
        clips = vast.get_video_vast(remote_username, remote_password, sudo_password, remote_path, start_time, end_time)
        clips = order_vast_file(clips)
    else:
        ns = NasStorage()
        clips = ns.get_video_nas(remote_username, remote_password, sudo_password, remote_path, prefix, start_time, end_time)
        clips = sorted(clips)


    for file_path in clips:
        ptl.logging_debug('[Video Continuous] file_path : {0}'.format(file_path))
        if pressure_test_video_type == 'medium':
            local_path = os.path.join("/mnt/", os.path.dirname(file_path).replace('//', '').replace('/', '_'))
            clippath = os.path.join(local_path, os.path.basename(file_path))
        else:
            local_path = os.path.join("/mnt/", remote_path.replace('//', '').replace('/', '_'))
            clippath = os.path.join(local_path, file_path.lower()[len(os.path.join(remote_path, "")):])

        recording_file_obj = RecordingFile.objects.filter(project_id =project_id,path=clippath)
        if len(recording_file_obj) <= 0:
            push_detect_broken_image_tasks_to_queue(remote_username, remote_password, str(project_id), remote_path, file_path, pressure_test_video_type, delay_time)
            time.sleep(5)


def push_detect_broken_image_tasks_to_queue(remote_username, remote_password, project_id, remote_path, file_path, pressure_test_video_type, delay_time):
    from libs.nas_storage import NasStorage
    from libs.vast_storage import VastStorage
    from recording_continous.models import Config
    from recording_continous.video_continous import VideoContinous
    from recording_continous.models import RecordingFile
    import os

    if pressure_test_video_type== 'medium':
        local_path = os.path.join("/mnt/", os.path.dirname(file_path).replace('//', '').replace('/', '_'))
        clippath = os.path.join(local_path, os.path.basename(file_path))
        vast = VastStorage()
        vast.mount_folder(remote_username, remote_password, remote_path, '', local_path)
    else:
        local_path = os.path.join("/mnt/", remote_path.replace('//', '').replace('/', '_'))
        clippath = os.path.join(local_path, file_path.lower()[len(os.path.join(remote_path, "")):])
        ns = NasStorage()
        ns.mount_folder(remote_username, remote_password, remote_path, '', local_path)

    query = RecordingFile.objects.filter(project_id=project_id)

    if len(query) > 0:
        query = RecordingFile.objects.filter(project_id=project_id).order_by('-id')[0]
        file_path_before = query.path
    else:
        file_path_before = 'first video'

    file_modify_time =  datetime.datetime.fromtimestamp(os.stat(clippath).st_mtime)
    file_size = str(int(os.path.getsize(clippath)/1000000))+' MB'
    RecordingFile.objects.create(
        project_id=project_id,
        modify_time=str(file_modify_time),
        size = file_size,
        path = clippath,

    )
    print("PUSH QUEUE:", clippath)
    vc = VideoContinous(file_path_before, clippath, delay_time)
    in_result = vc.continuity_in_recording_files(project_id)

    if 'first video' not in file_path_before:
        between_result = vc.continuity_bwtween_recording_files(project_id)
    else :
        between_result ={}
        between_result["between_result"] = '-'
        between_result["seconds"] = 'First video'

    if pressure_test_video_type == 'high':
        video_path_result = file_path.replace(remote_path+"/", "")
    else:
        video_path_result = clippath.replace(local_path + "/", "")

    if in_result["in_result"] != "pass":
        # error_txt_link = "ftp://{0}:{1}@{2}/{3}/continous_error".format(remote_username,remote_password,remote_path.replace("//",""),os.path.dirname(video_path_result))
        error_txt_link = "ftp://{0}:{1}@{2}continous_error".format(remote_username, remote_password, os.path.dirname(file_path).replace('//', ''))

    else:
        error_txt_link = ""

    RecordingContinuty.objects.create(
        project_id=project_id,
        creat_at=str(file_modify_time),
        video_path=video_path_result,
        video_path_before=file_path_before.replace(local_path+"/", ""),
        size=file_size,
        in_result=in_result["in_result"],
        error_code=in_result["error_code"],
        start_time=in_result["start_time"],
        end_time=in_result["end_time"],
        link=error_txt_link,
        count=in_result["count"],
        between_result=between_result["between_result"],
        seconds=between_result["seconds"],
        )

def order_vast_file(clips):
    clips_timelist = []
    sorted_filelist = []

    for file_path in clips:
        local_path = os.path.join("/mnt/", os.path.dirname(file_path).replace('//', '').replace('/', '_'))
        clippath = os.path.join(local_path, os.path.basename(file_path))

        clip_modify_time = os.stat(clippath).st_mtime
        # clips_dictionary[file_path] = datetime.datetime.fromtimestamp(os.stat(clippath).st_mtime)
        clips_timelist.append([clip_modify_time, file_path])

    for i in sorted(clips_timelist):
        sorted_filelist.append(i[1])
    return sorted_filelist

def order_nas_file(clips, remote_path):
    clips_timelist = []
    sorted_filelist = []

    for file_path in clips:
        local_path = os.path.join("/mnt/", remote_path.replace('//', '').replace('/', '_'))
        clippath = os.path.join(local_path, file_path.lower()[len(os.path.join(remote_path, "")):])

        clip_modify_time = os.stat(clippath).st_mtime
        # clips_dictionary[file_path] = datetime.datetime.fromtimestamp(os.stat(clippath).st_mtime)
        clips_timelist.append([clip_modify_time, file_path])

    for i in sorted(clips_timelist):
        sorted_filelist.append(i[1])
    return sorted_filelist
