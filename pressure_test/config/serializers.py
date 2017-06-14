from rest_framework import serializers
from config.models import ProjectSetting


class ProjectSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSetting
        fields = ('project_name', 'prefix_name', 'start_time', 'end_time', 'owner', 'ip', 'username', 'password', 'type', 'path', 'path_username',
                    'path_password', 'broken', 'continued', 'log', 'cgi', 'delay')