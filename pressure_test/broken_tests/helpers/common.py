import os
import subprocess


class Video(object):
    def __init__(self, filename):
        """

        Keyword arguments:
        filename -- the string of filename of video
                    supported file extenstion and codec as same as ffmpeg.
        """
        self.__filename = filename

    def to_single_frame(self, timestamp, out_filename):
        """Output single frame from video sequence at timestamp.

        Keyword arguments:
        timestamp -- the string of wanted time (format 00:00:14.435)
        out_filename -- the string of output filename
                        supported file extenstion as same as ffmpeg.
        """
        if not os.path.exists(os.path.dirname(out_filename)):
            os.makedirs(os.path.dirname(out_filename))

        # ffmpeg -i input.flv -ss 00:00:14.435 -vframes 1 out.png
        cmd = "ffmpeg -i {} -ss {} -vframes 1 {}".format(self.__filename, timestamp, out_filename)
        print(cmd)
        subprocess.check_output(cmd, shell=True)

    def to_multi_frames(self, fps, out_filename):
        """Output multiple frames from video sequence by fps.

        Keyword arguments:
        fps -- the number of output frame rate
        out_filename -- the regex string of output filenames (format out%02d.jpg)
                        supported file extenstion as same as ffmpeg.
        """
        if not os.path.exists(os.path.dirname(out_filename)):
            os.makedirs(os.path.dirname(out_filename))

        # ffmpeg -i input.flv -vf fps=1 out%d.png
        cmd = "ffmpeg -i {} -vf fps={} {}".format(self.__filename, fps, out_filename)
        print(cmd)
        subprocess.check_output(cmd, shell=True)

    def to_all_frames(self, out_filename):
        """Output all frames from video sequence.

        Keyword arguments:
        out_filename -- the regex string of output filenames (format out%02d.jpg)
                        supported file extenstion as same as ffmpeg.
        """
        if not os.path.exists(os.path.dirname(out_filename)):
            os.makedirs(os.path.dirname(out_filename))

        # ffmpeg -i input.flv -vsync vfr out%d.png
        cmd = "ffmpeg -i {} -vsync vfr {}".format(self.__filename, out_filename)
        print(cmd)
        subprocess.check_output(cmd, shell=True)

    # def to_duration_frames(self, start_at, time_limit, fps, out_filename):
    #     """Output multiple frames by defining start time, interval and fps from video sequence.
    #
    #     Keyword arguments:
    #     start_at -- the integer of seconds to seek by timestamp with position in input file.
    #     time_limit -- the interger of seconds to exit after ffmpeg has been running for such seconds.
    #     out_filename -- the regex string of output filenames (format out%02d.jpg)
    #                     supported file extenstion as same as ffmpeg.
    #     """
    #     if not os.path.exists(os.path.dirname(out_filename)):
    #         os.makedirs(os.path.dirname(out_filename))
    #
    #     # ffmpeg -ss 10 -timelimit 1 -i input.flv -vf fps=1 out%d.png
    #     cmd = "ffmpeg -ss {} -timelimit {} -i {} -vf fps={} {}".format(start_at, time_limit, self.__filename, fps, out_filename)
    #
    #     subprocess.call(cmd, shell=True)

    def to_duration_frames(self, start_at, fps, frame_num, out_filename):
        """Output multiple frames by defining start time, interval and fps from video sequence.

        Keyword arguments:
        start_at -- the integer of seconds to seek by timestamp with position in input file.
        frame_num -- the string of frame_num that the number of frames you need.
        time_limit -- the interger of seconds to exit after ffmpeg has been running for such seconds.
        out_filename -- the regex string of output filenames (format out%02d.jpg)
                        supported file extenstion as same as ffmpeg.
        """
        if not os.path.exists(os.path.dirname(out_filename)):
            os.makedirs(os.path.dirname(out_filename))

        #ffmpeg -i medium_stress09.mp4 -an -ss 00:00:55 -r 2 -vframes 20 -y img%d.jpg
        cmd = "ffmpeg -i {} -an -ss {} -r {} -vframes {} -y {}".format(self.__filename, start_at, fps, frame_num, out_filename)
        print(cmd)
        subprocess.call(cmd, shell=True)

    def crop(self, out_x, out_y, out_w, out_h, out_filename):
        """Output a cropped video.

        Keyword arguments:
        out_x, out_y -- the position of the top left corner starting to the output rectangle
        out_w -- the width of the output rectangle
        out_h -- the height of the output rectangle
        out_filename -- the string of output filename
        """

        if not os.path.exists(os.path.dirname(out_filename)):
            os.makedirs(os.path.dirname(out_filename))

        #  ffmpeg -i test02.mp4 -filter:v "crop=1000:50:0:0" -c:a copy out.mp4
        cmd = "ffmpeg -i {} -filter:v \"crop={}:{}:{}:{}\" -c:a copy {}".format(self.__filename, out_x, out_y, out_w, out_h, out_filename)
        print(cmd)
        subprocess.check_output(cmd, shell=True)
