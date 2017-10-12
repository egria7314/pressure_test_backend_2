from django.http import HttpResponse
from django.shortcuts import render_to_response
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions

import os

# Create your views here.
@api_view(['GET'])
def get_version(requests):
    print(os.environ.get('PATH'))
    print(os.environ.get('CLASSPATH'))
    return Response({"version":"v1.0.9"})