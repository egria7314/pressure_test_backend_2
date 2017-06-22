from recording_continous.views import continous_running_status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from config.models import ProjectSetting


@api_view(['GET'])
def monitor_alive(request):
    project_id = request.GET['project_id']
    continuous = continous_running_status(project_pk=project_id)['status']
    ProjectSetting.objects.filter(id=project_id).update(continuity_status=continuous)

    return Response(continuous)