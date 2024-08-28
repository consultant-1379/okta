from __future__ import unicode_literals
from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from utils import meteoFunctions

@login_required(login_url='/')
def cloud_stats(request):
    clouds_info = meteoFunctions.get_clouds_info()
    projects_breakdown = meteoFunctions.get_projects_breakdown_info()
    program_allocation_info = meteoFunctions.get_resource_allocation_by_program()
    returned_projects_info = meteoFunctions.get_returned_projects(21)
    
    context = {
        "clouds": clouds_info,
        "projects_breakdown": projects_breakdown,
        "program_allocation_info": program_allocation_info,
        "returned_projects_info": returned_projects_info
        }
    
    print(context)
    return render(request, "cloudstats/cloud-stats.html", context)
