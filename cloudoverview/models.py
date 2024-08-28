from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class PotentialCloud(models.Model):
    cloud_name = models.CharField(max_length=32, blank=False, null=False, unique=True)
    version = models.CharField(max_length=32, blank=True, null=False)
    number_of_hosts = models.IntegerField(blank=False, null=False)
    cpu_contention = models.FloatField(max_length=32, blank=False, null=False)
    total_cpu = models.FloatField(max_length=32, blank=False, null=False)
    ram_contention = models.FloatField(max_length=32, blank=False, null=False)
    total_ram = models.FloatField(max_length=32, blank=False, null=False)
    storage = models.FloatField(max_length=32, blank=False, null=False)
    provisioning = models.CharField(max_length=32, blank=True)
    
    def save(self, *args, **kwargs):
        return super(PotentialCloud, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.cloud_name)
