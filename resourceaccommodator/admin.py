# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *

class OrderableItemAdmin(admin.ModelAdmin):
    list_display = ('orderable_item_name', 'self_managed', 'vcpu', 'ram', 'volume_storage', 'total_vm_count', 'director_node_count', 'director_vcpu', 'director_ram', 'master_node_count', 'master_vcpu', 'master_ram', 'worker_app_node_count', 'worker_app_vcpu', 'worker_app_ram', 'worker_net_node_count', 'worker_net_vcpu', 'worker_net_ram', 'nfs_server_node_count', 'nfs_server_vcpu', 'nfs_server_ram', 'cENM_client_node_count', 'cENM_client_vcpu', 'cENM_client_ram','total_node_count', 'total_vcpu', 'total_ram', 'ecfe_ip_count', 'static_ip_count', 'nfs_required', 'workers_affinity_rule', 'master_flavor', 'master_root_volume_size', 'master_root_config_volume_size', 'director_flavor', 'director_root_volume_size', 'director_config_volume_size', 'container_registry_storage_size', 'worker_flavor', 'worker_root_volume_size')
admin.site.register(OrderableItem, OrderableItemAdmin)


class CloudAdmin(admin.ModelAdmin):
    list_display = ('cloud_name', 'number_of_hosts', 'physical_cpu_host', 'cpu_contention', 'total_cpu', 'ram_per_host', 'ram_contention', 'total_ram', 'storage', 'ecfe_ips', 'static_ips')
admin.site.register(Cloud, CloudAdmin)