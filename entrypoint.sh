#!/bin/bash

ansible-playbook /home/dqa/data/setup_of_django_settings.yml -i /home/dqa/data/hosts
/home/dqa/code/env/bin/python /home/dqa/data/pressure_test/manage.py runserver 0.0.0.0:8000
