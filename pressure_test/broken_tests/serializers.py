from rest_framework import serializers
from broken_tests.models import ClipInfo, NasProfile, CameraProfile, BrokenFrame


class NasProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = NasProfile
        fields = ('id', 'user', 'password', 'location', 'workgroup')

class CameraProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraProfile
        fields = ('id', 'host', 'user', 'password')

class BrokenFrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrokenFrame
        fields = ('id', 'error_message', 'frame_path', 'timestamp')

class ClipInfoSerializer(serializers.ModelSerializer):
    broken_frames = BrokenFrameSerializer(many=True)
    
    result = serializers.ReadOnlyField()
    count = serializers.ReadOnlyField()
    link = serializers.ReadOnlyField()
    errorCode = serializers.ReadOnlyField()
    path = serializers.ReadOnlyField()

    class Meta:
        model = ClipInfo
        fields = ('id', 'path', 'full_path', 'size', 'privacy_masks', 'is_broken', 'result', 'errorCode', 'count', 'link', 'broken_frames')