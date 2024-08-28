from __future__ import unicode_literals
from django.shortcuts import render,get_object_or_404
from bootstrap_modal_forms.generic import BSModalCreateView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import PotentialCloudModelForm
from .models import PotentialCloud
from django.http import JsonResponse
from utils import meteoFunctions
from django.http import HttpResponseRedirect

@login_required(login_url='/')
def cloud_overview(request):
    clouds_info = meteoFunctions.get_clouds_info()
    cloud_capacity_data = meteoFunctions.get_cloud_capacity_data()
    context = {
        "clouds": clouds_info,
        "potential_clouds": PotentialCloud.objects.filter(),
        "cloud_capacity_data": cloud_capacity_data
        }
    
    return render(request, "cloudoverview/cloud-overview.html", context)
   
class PotentialCloudCreateView(BSModalCreateView):
    template_name = 'cloudoverview/create_potential_cloud.html'
    form_class = PotentialCloudModelForm
    success_message = 'Success: Potential Cloud was created.'
    success_url = reverse_lazy('cloudoverview:cloud-overview')

def get_potential_cloud_api(request):
    cloud_name = request.GET.get('potential_cloud')
    potential_cloud = list(PotentialCloud.objects.filter(cloud_name=cloud_name).values())[0]
    
    return JsonResponse({"potential_cloud": potential_cloud}, safe=False)


def delete_potential_cloud(request):
    id = request.GET.get('id')
    potential_cloud = PotentialCloud.objects.get(id=id)

    potential_cloud.delete()
    return HttpResponseRedirect("/cloud-overview")


def get_edit_potential_cloud_modal(request):
    print("get_edit")
    id = request.GET.get('id')
    potential_cloud = PotentialCloud.objects.get(id=id)
    context = {
        "cloud": potential_cloud
        }
    return render(request, "cloudoverview/edit-potential-cloud-modal.html", context)


def edit_potential_cloud(request):
    changes = {}
    id = request.POST.get("id")
    changes["cloud_name"] = request.POST.get("cloud_name") if request.POST.get("cloud_name") else None
    changes["version"] = request.POST.get("version") if request.POST.get("version") else None
    changes["total_cpu"] = request.POST.get("cpu") if request.POST.get("cpu") else None
    changes["cpu_contention"] = request.POST.get("cpu_contention") if request.POST.get("cpu_contention") else None
    changes["ram_contention"] = request.POST.get("ram_contention") if request.POST.get("ram_contention") else None
    changes["total_ram"] = request.POST.get("ram") if request.POST.get("ram") else None
    changes["storage"]= request.POST.get("storage") if request.POST.get("storage") else None
    changes["number_of_hosts"] = request.POST.get("number_of_hosts") if request.POST.get("number_of_hosts") else None
    changes["provisioning"] = request.POST.get("provisioning") if request.POST.get("provisioning") else None

    response = {}
    potential_cloud = PotentialCloud.objects.get(id=id)
    for key in changes:
        if changes[key]:
            try:
                setattr(potential_cloud, key, changes[key])
            except Exception as e:
                response[key] = str(e)

    potential_cloud.save()
    if not response:
        response["Message"] = "Success"


    return HttpResponseRedirect("/cloud-overview")







