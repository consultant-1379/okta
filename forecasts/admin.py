from django.contrib import admin

#@admin.register(PotentialCloud) #customizing the way to work with the models in the admin
#class PotentialCloudAdmin(admin.ModelAdmin):
#    list_display = ('cloud_name', 'version', 'number_of_hosts', 'cpu_contention', 'total_cpu', 'ram_contention', 'total_ram', 'storage', 'provisioning')