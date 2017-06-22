from recording_continous.views import continous_running_status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import json

# @api_view(['GET'])
# def monitor_alive(request):
#     continuous = continous_running_status()
#     json.dumps(broken)
#
#     return Response(json.dumps(broken))