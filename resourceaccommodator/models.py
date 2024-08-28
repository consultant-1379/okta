from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager

# Create your models here.

class OrderableItem(models.Model):
    orderable_item_name = models.CharField(max_length=64, blank=True, default="", unique=True, primary_key=True)
    self_managed = models.BooleanField(default=False)
    vcpu = models.CharField(max_length=32, blank=True, null=True)
    ram = models.CharField(max_length=32, verbose_name="Total RAM (GB):", blank=True, null=True)
    volume_storage = models.CharField(max_length=32, verbose_name="Total Volume Storage (GB):", blank=True,
                                            null=True)
    total_vm_count = models.CharField(max_length=32, blank=True, null=True)
    
    director_node_count = models.CharField(max_length=32, blank=True, null=True)
    director_vcpu = models.CharField(max_length=32, blank=True, null=True)
    director_ram = models.CharField(max_length=32, blank=True, null=True)

    master_node_count = models.CharField(max_length=32, blank=True, null=True)
    master_vcpu = models.CharField(max_length=32, blank=True, null=True)
    master_ram = models.CharField(max_length=32, blank=True, null=True)    

    worker_app_node_count = models.CharField(max_length=32, blank=True, null=True)
    worker_app_vcpu = models.CharField(max_length=32, blank=True, null=True)
    worker_app_ram = models.CharField(max_length=32, blank=True, null=True)
    
    worker_net_node_count = models.CharField(max_length=32, blank=True, null=True)
    worker_net_vcpu = models.CharField(max_length=32, blank=True, null=True)
    worker_net_ram = models.CharField(max_length=32, blank=True, null=True)
    
    nfs_server_node_count = models.CharField(max_length=32, blank=True, null=True)
    nfs_server_vcpu = models.CharField(max_length=32, blank=True, null=True)
    nfs_server_ram = models.CharField(max_length=32, blank=True, null=True)  
    
    cENM_client_node_count = models.CharField(max_length=32, blank=True, null=True)
    cENM_client_vcpu = models.CharField(max_length=32, blank=True, null=True)
    cENM_client_ram = models.CharField(max_length=32, blank=True, null=True)  
    
    total_node_count = models.CharField(max_length=32, blank=True, null=True)
    total_vcpu = models.CharField(max_length=32, blank=True, null=True)
    total_ram = models.CharField(max_length=32, blank=True, null=True)    
    
    ecfe_ip_count = models.CharField(max_length=32, blank=True, null=True)
    static_ip_count = models.CharField(max_length=32, blank=True, null=True)
    nfs_required = models.BooleanField(default=False)
    workers_affinity_rule = models.BooleanField(default=False)

    master_flavor = models.CharField(max_length=32, blank=True, null=True)
    master_root_volume_size = models.CharField(max_length=32, blank=True, null=True)
    master_root_config_volume_size = models.CharField(max_length=32, blank=True, null=True)

    director_flavor = models.CharField(max_length=32, blank=True, null=True)
    director_root_volume_size = models.CharField(max_length=32, blank=True, null=True)
    director_config_volume_size = models.CharField(max_length=32, blank=True, null=True)

    container_registry_storage_size = models.CharField(max_length=32, blank=True, null=True)
    worker_flavor = models.CharField(max_length=32, blank=True, null=True)
    worker_root_volume_size = models.CharField(max_length=32, blank=True, null=True)

    
    def save(self, *args, **kwargs):
        # On save, update timestamps
        #if not self.id:
        #    self.created = django.utils.timezone.now()
        #self.modified = django.utils.timezone.now()
        return super(OrderableItem, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.orderable_item_name)
    
class Cloud(models.Model):
    cloud_name = models.CharField(max_length=32, blank=True, null=True, unique=True)
    number_of_hosts = models.CharField(max_length=32, blank=True, null=True)
    physical_cpu_host =models.CharField(max_length=32, blank=True, null=True)
    cpu_contention = models.CharField(max_length=32, blank=True, null=True)
    total_cpu = models.CharField(max_length=32, blank=True, null=True)
    ram_per_host = models.CharField(max_length=32, blank=True, null=True)
    ram_contention = models.CharField(max_length=32, blank=True, null=True)
    total_ram = models.CharField(max_length=32, blank=True, null=True)
    storage = models.CharField(max_length=32, blank=True, null=True)
    ecfe_ips = models.CharField(max_length=32, blank=True, null=True)
    static_ips = models.CharField(max_length=32, blank=True, null=True)

    
    def save(self, *args, **kwargs):
        # On save, update timestamps
        #if not self.id:
        #    self.created = django.utils.timezone.now()
        #self.modified = django.utils.timezone.now()
        return super(Cloud, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.cloud_name)
