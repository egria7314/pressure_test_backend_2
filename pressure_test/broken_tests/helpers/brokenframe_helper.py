# -*- coding: utf-8 -*-
from broken_tests.models import BrokenFrame, ClipInfo
import re
import datetime
import os

class BrokenFrameHelper(object):
    def __init__(self, clipid):
        self.clip = ClipInfo.objects.get(id=clipid)    # ClipInfo object


    def batch_create_db(self, video_status):
        """
        ex: video_status = {
            'result': 'failed',
            'failed_frames': [
                {
                    'error_message': "decoede error",
                    'path': "a/b/c.mp4"
                },
                {
                    'error_message': "decoede error",
                    'path': "a/b/c.mp4"
                },
            ] }
        """
        for failed_frame in video_status['failed_frames']:
            print("each failed frame: ", failed_frame)
            m = re.search(r"mul(?P<timestamp>[0-9]+).jpg", failed_frame['path'])
            if m:
                seq_to_seconds = round(int(m.group('timestamp'))/2, 1) # 2: fps
                timestamp = datetime.timedelta(seconds=seq_to_seconds)
                # replace broken frame path with timestamp
                renamed_path = failed_frame['path'].replace(
                    'mul'+m.group('timestamp'),
                    str(timestamp).replace(":", "'")
                )
                os.rename(failed_frame['path'], renamed_path)
                failed_frame['path'] = renamed_path
            else:
                timestamp = None

            BrokenFrame.objects.create(
                error_message=failed_frame['error_message'],
                frame_path=failed_frame['path'],
                clip=self.clip,
                timestamp=timestamp
            )