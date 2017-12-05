# -*- coding: utf-8 -*-
# Create your models here.
from django.db import models
class Email_server_private_parameter(models.Model):
    owner = models.CharField(max_length=50 ,blank=True)
    server_i0_email_senderemail = models.CharField(max_length=50 ,blank=True)
    server_i0_email_recipientemail = models.CharField(max_length=50 , blank=True)
    server_i0_email_address = models.CharField(max_length=50, blank=True)
    server_i0_email_username = models.CharField(max_length=50, blank=True)
    server_i0_email_passwd = models.CharField(max_length=50, blank=True)
    server_i0_email_port = models.CharField(max_length=50, blank=True)
    server_i0_email_sslmode = models.CharField(max_length=50, blank=True)

class Ftp_server_private_parameter(models.Model):
    test_type = models.CharField(max_length=50, default='')
    location = models.CharField(max_length=50, default='')
    owner = models.CharField(max_length = 50)
    server_i1_ftp_address = models.CharField(max_length=50)
    server_i1_ftp_username = models.CharField(max_length=50)
    server_i1_ftp_passwd = models.CharField(max_length=50)
    server_i1_ftp_location = models.CharField(max_length=50)


class Nas_server_private_parameter(models.Model):
    test_type = models.CharField(max_length=50, default='')
    location = models.CharField(max_length=50, default='')
    owner = models.CharField(max_length = 50)
    server_i2_ns_location = models.CharField(max_length=50)
    server_i2_ns_workgroup = models.CharField(max_length=50)
    server_i2_ns_username = models.CharField(max_length=50)
    server_i2_ns_passwd = models.CharField(max_length=50)









