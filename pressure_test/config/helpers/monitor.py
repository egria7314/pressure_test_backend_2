# from broken_tests.views import
from rest_framework.response import Response
from rest_framework.decorators import api_view
import json

# @api_view(['GET'])
# def monitor_alive(request):
#     broken = Monitor().get_schedule_status()
#     json.dumps(broken)
#
#     return Response(json.dumps(broken))