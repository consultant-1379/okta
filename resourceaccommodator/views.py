from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from collections import OrderedDict, defaultdict, Counter
import json,requests,re, os, sys
from .models import *
from bs4 import BeautifulSoup
from cloudoverview.models import *
from utils.meteoFunctions import get_ccd_projects_info as get_ccd_projects_info
from utils.meteoFunctions import get_clouds_info as get_clouds_info
from utils.meteoFunctions import get_cloud_info as get_cloud_info
from utils.meteoFunctions import get_self_managed_ccd_data as get_self_managed_ccd_data
from utils.meteoFunctions import get_all_deployment_type_resources as get_all_deployment_type_resources
vcpu_increase = 0
ram_increase = 0

@csrf_exempt
@login_required(login_url='/')
def resource_accommodator(request):
    orderable_items = OrderableItem.objects.all().order_by('orderable_item_name')
    potential_clouds = PotentialCloud.objects.all().order_by('cloud_name')
    existing_clouds = get_clouds_info()
    deployment_type_resources = get_all_deployment_type_resources()
    ccd_projects_dict = get_ccd_projects_info()
    ccd_projects = ccd_projects_dict['ccd_projects']
    cloud_and_ccd_flavors = defaultdict(list)
    for project in ccd_projects:
        if (project['ccd_flavor'].startswith("cus") or project['ccd_flavor'].startswith("ga_")):
            ccd_flavor = project['ccd_flavor'].split('_')[0] + "-" + project['ccd_flavor'].split('_')[1]
            cloud_and_ccd_flavors[project['cloud']].append(ccd_flavor)
        else:
            cloud_and_ccd_flavors[project['cloud']].append(project['ccd_flavor'].split('_')[0])
    
    ccd_breakdown_ord_dict=OrderedDict()
    for cloud, ccd_flavor in cloud_and_ccd_flavors.items():
        qty_ccd_flavors_in_cloud = []
        unique_ccd_flavors_in_cloud = set(ccd_flavor)
        for flav in unique_ccd_flavors_in_cloud:
            qty_ccd_flavors_in_cloud.append(str(flav))
            qty_ccd_flavors_in_cloud.append(ccd_flavor.count(flav))
        ccd_breakdown_ord_dict[cloud] = qty_ccd_flavors_in_cloud
    ccd_breakdown=json.dumps(ccd_breakdown_ord_dict)
    
    #existing_clouds = get_clouds_info()
    return render(request, "resourceaccommodator/resource-accommodator.html", {"orderable_items": orderable_items, "potential_clouds": potential_clouds, "existing_clouds": existing_clouds, "ccd_breakdown": ccd_breakdown, "deployment_type_resources": deployment_type_resources})

def get_orderable_item():
    orderable_items = {}
    username = 'protoadm10'
    password = 'vFc214db8TycS6522'
    session = requests.Session()
    session.auth = (username, password)
    page_titles=["DE-CNI++-+cENM+General+Availability+%28GA%29+Usage+CCD+Orderable+Items", "DE-CNI++-+ECSON+General+Availability+%28GA%29+Usage+CCD+Orderable+Items", \
                 "DE-CNI++-+ENIQS+CCD+Deployments+Requirements", "DE-CNI++-+iDUN+General+Availability+%28GA%29+Usage+CCD+Orderable+Items", \
                 "DE-CNI++-+Pathfinder++CCD+Deployments+Requirements", "DE-CNI++-++SWDP+CCD+Deployments+Requirements", "DE-CNI+-+EO+General+Availability+%28GA%29+Usage+CCD+Orderable+Items", \
                 "DE-CNI+-+DE-CNI+General+Availability+%28GA%29+Usage+CCD+Orderable+Items"]
    #page_titles=["DE-CNI+-+EO+Limited+Availability+%28LA%29+Usage+CCD+Orderable+Items"]
    for title in page_titles:
        url = "https://confluence-oss.seli.wh.rnd.internal.ericsson.com/pages/viewpage.action?spaceKey=CIE&title=" + title
        try:
            response = session.get(url)
        except Exception as e:
            print("Unable to make a connection: " + e + "URl: " + url)
        soup = BeautifulSoup(response.content, 'lxml')
        if title == "DE-CNI+-+DE-CNI+General+Availability+%28GA%29+Usage+CCD+Orderable+Items" or title == "DE-CNI+-+EO+General+Availability+%28GA%29+Usage+CCD+Orderable+Items" \
        or title == "DE-CNI+-+EO+Limited+Availability+%28LA%29+Usage+CCD+Orderable+Items":
            orderable_items = soup.find_all('h2')
            count=1
        elif title == "DE-CNI++-+cENM+General+Availability+%28GA%29+Usage+CCD+Orderable+Items" or title == "DE-CNI++-+ECSON+General+Availability+%28GA%29+Usage+CCD+Orderable+Items" \
        or title == "DE-CNI++-+iDUN+General+Availability+%28GA%29+Usage+CCD+Orderable+Items":
            orderable_items = soup.find_all('h1')
            del orderable_items[:1]
            count=2
        else:
            orderable_items = soup.find_all('h1')
            del orderable_items[:2]
            #Set count so the corresponding project info can be gathered
            count=1
        
        for heading in orderable_items:
            if not heading.getText():
                orderable_items.remove(heading)
        
        #count=1
        for item in orderable_items:
            vcpu = "0"
            ram = "0"
            volume_storage = "0"
            total_vm_count = "0"
            director_node_count="0"
            director_vcpu="0"
            director_ram="0"
            master_node_count="0" 
            master_vcpu="0"
            master_ram="0"
            worker_app_node_count="0" 
            worker_app_vcpu="0"
            worker_app_ram="0" 
            worker_net_node_count="0"
            worker_net_vcpu="0"
            worker_net_ram="0"
            nfs_server_node_count="0"
            nfs_server_vcpu="0"
            nfs_server_ram="0"
            total_node_count="0" 
            total_vcpu="0"
            total_ram="0"
            cENM_client_node_count="0"
            cENM_client_vcpu="0"
            cENM_client_ram="0"
            # format for below Orderable Items was all over the place, EO confluence page is to be audited in next sprint (21.8) so revisit once completed 
            if (item.getText().startswith("STD-EO1-B") and item.getText().endswith("(Production Environment)")) or item.getText().startswith("ARCHIVED") :
                count+=1
            if item.getText().startswith("(Flexikube)") or item.getText().startswith("EO9") or item.getText().startswith("EO13-A")\
            or item.getText().startswith("EO13-B") or item.getText().startswith("EO13-C") or item.getText().startswith("EO30") or "Free space" in item.getText() \
            or item.getText().startswith("UPGRADE") or (item.getText().startswith("STD-EO1-B") and item.getText().endswith("(Test Environment)")) :
                project_info = soup.find_all('div', {"class": "innerCell"})[count]
                count+=1
                continue
            elif item.getText().startswith("Guideline") or item.getText().startswith("EO10") or item.getText().startswith("EO21-Cloud11") or item.getText().startswith("Order") \
            or item.getText().startswith("Appendix") or item.getText().startswith("<") :
                continue
                
            #cENM7 has 3 different types, look into this
            if(item.getText().startswith("cENM7")):
                orderable_item_name = item.getText() 
            elif(item.getText().startswith("EO16") and "-" in item.getText()):
                 orderable_item_name = (item.getText().replace('-', '')).split()[0]
            elif(item.getText().startswith("Director") or item.getText().startswith("Master") or item.getText().startswith("Worker")):
                continue
            else:
                orderable_item_name = item.getText().split()[0]
            project_info = soup.find_all('div', {"class": "innerCell"})[count]
            print(orderable_item_name)
            #print(project_info)
            
            if "ECSON" in title:
                if item.getText().endswith("ECSON3"):
                    project_resources=project_info.find_all('p')[2].getText().split()
                    vcpu = project_resources[1][:-4]
                    ram = project_resources[2]
                    volume_storage = project_resources[4]
                elif item.getText().startswith("ECSON3-A"):
                    table=project_info.find_all('table')[1]
                    table_rows= table.find_all('tr')
                    for row in table_rows:
                        resource = row.find_all('td')[0].string
                        if resource == None:
                            continue
                        elif resource == "vCPU":
                            vcpu = row.find_all('td', {"class": "confluenceTd"})[1].string.strip()
                        elif resource.startswith("RAM"):
                            ram = row.find_all('td', {"class": "confluenceTd"})[1].string.strip()
                        elif resource.startswith("Total Volume"):
                            volume_storage = row.find_all('td', {"class": "confluenceTd"})[1].string.strip()
                else:
                    project_resources=project_info.find_all('p')[3].getText().split()
                    vcpu = project_resources[1]
                    ram = project_resources[3]
                    volume_storage = project_resources[6]
                    total_vm_count = project_resources[15] 
            elif "iDUN" in title or "Pathfinder" in title:
                if item.getText().startswith("IDUN2"):
                    project_resources=project_info.find_all('p')[3].getText().split()
                    vcpu = project_resources[1]
                    ram = project_resources[3]
                    volume_storage = project_resources[6]
                    total_vm_count = project_resources[12]
                else:
                    vcpu_val = project_info.find("pre").contents[0]
                    vcpu_list = [int(s) for s in vcpu_val.split() if s.isdigit()]
                    vcpu = vcpu_list[0]
                    ram_val = project_info.find("pre").contents[2]
                    ram_list = [int(s) for s in ram_val.split() if s.isdigit()]
                    ram = ram_list[0]
                    vol_val = project_info.find("pre").contents[4]
                    volume_storage_list = [int(s) for s in vol_val.split() if s.isdigit()]
                    volume_storage = volume_storage_list[0]
                    vm_val = project_info.find("pre").contents[6]
                    total_vm_count_list = [int(s) for s in vm_val.split() if s.isdigit()]
                    total_vm_count = total_vm_count_list[0]
            #Works for Standard EO page
            elif "EO" in title or "Usage" in title or ("cENM" in title and item.getText().endswith("dimensioning)")) or (item.getText().startswith("cENM5") and item.getText().endswith("IBD")) \
            or item.getText().endswith("EVNFM") or item.getText().endswith("EVNFM)") or orderable_item_name == "cENM1" or orderable_item_name == "cENM4":
                
                if orderable_item_name == "CUS-EO2" or orderable_item_name == "CUS-EO18":
                    table = project_info.find_all('table')[2]
                else:
                    table = project_info.find_all('table')[1]
                table_rows= table.find_all('tr')
                if (orderable_item_name == "cENM10-B"):
                    vcpu_val = project_info.find("pre").contents[0]
                    vcpu_list = [int(s) for s in vcpu_val.split() if s.isdigit()]
                    vcpu = vcpu_list[0]
                    ram_val = project_info.find("pre").contents[2]
                    ram_list = [int(s) for s in ram_val.split() if s.isdigit()]
                    ram = ram_list[0]
                    vol_val = project_info.find("pre").contents[4]
                    volume_storage_list = [int(s) for s in vol_val.split() if s.isdigit()]
                    volume_storage = volume_storage_list[0]
                    vm_val = project_info.find("pre").contents[6]
                    total_vm_count_list = [int(s) for s in vm_val.split() if s.isdigit()]
                    total_vm_count = total_vm_count_list[0]
                else:
                    for row in table_rows:
                        resource = row.find_all('td')[0].string
                        if resource == None:
                            continue
                        elif resource == "vCPU":
                            vcpu = row.find_all('td', {"class": "confluenceTd"})[1].string.strip()
                        elif resource.startswith("RAM"):
                            ram = row.find_all('td', {"class": "confluenceTd"})[1].string.strip()
                        elif resource.startswith("Total Volume"):
                            volume_storage = row.find_all('td', {"class": "confluenceTd"})[1].string.strip()
            #Works for the SWDP page
            elif "SWDP" in title:
                vcpu = project_info.find_all('p')[1].string
                vcpu_val = re.findall(r'\b\d+\b', vcpu)
                vcpu = vcpu_val[0]
                info = project_info.find_all('p')[2]
                values = re.findall(r'\b\d+\b', info.getText())
                ram = values[0]
                volume_storage = values[1]
                total_vm_count = values[2]
            #Works for Eniq page
            elif "ENIQS" in title:
                project_resources=project_info.find_all('p')[4].getText().split()
                vcpu = project_resources[1]
                ram = project_resources[3]
                if item.getText() == "ENIQS3":
                    volume_storage = int(project_resources[6])*1000
                else:
                    volume_storage = project_resources[6]
            #Works for ECSON
            
            #cENM
            elif "cENM" in title:
                #print(project_info)
                if item.getText().startswith("cENM5") or item.getText().startswith("cENM7") \
                or item.getText().startswith("cENM8") or item.getText().startswith("cENM10"):
                    vcpu_val = project_info.find("pre").contents[0]
                    vcpu_list = [int(s) for s in vcpu_val.split() if s.isdigit()]
                    vcpu = vcpu_list[0]
                    ram_val = project_info.find("pre").contents[2]
                    ram_list = [int(s) for s in ram_val.split() if s.isdigit()]
                    ram = ram_list[0]
                    vol_val = project_info.find("pre").contents[4]
                    volume_storage_list = [int(s) for s in vol_val.split() if s.isdigit()]
                    volume_storage = volume_storage_list[0]
                    vm_val = project_info.find("pre").contents[6]
                    total_vm_count_list = [int(s) for s in vm_val.split() if s.isdigit()]
                    if total_vm_count_list:
                        total_vm_count = total_vm_count_list[0]
                elif item.getText().strip().startswith("cENM4"):
                    project_resources=project_info.find_all('p')[3].getText().split()
                    vcpu = project_resources[1]
                    vcpu = vcpu[:-4]
                    ram = project_resources[2]
                    volume_storage = project_resources[4]
                elif item.getText().strip().startswith("cENM2"):
                    vcpu_resources=project_info.find_all('p')[3].getText().split()
                    vcpu=vcpu_resources[1]
                    project_resources=project_info.find_all('p')[4].getText().split()
                    ram = project_resources[1]
                    volume_storage = project_resources[4]
                    total_vm_count = project_resources[6]
                elif item.getText().strip().startswith("cENM9"):
                    vcpu_val = project_info.find("pre").contents[0]
                    vcpu_list = [int(s) for s in vcpu_val.split() if s.isdigit()]
                    vcpu = vcpu_list[0]
                    ram_val = project_info.find("pre").contents[2]
                    ram_list = [int(s) for s in ram_val.split() if s.isdigit()]
                    ram = ram_list[0]
                    vol_val = project_info.find("pre").contents[4]
                    volume_storage = int(float(re.findall("\d+\.\d+", vol_val)[0])*1000)
                    vm_val = project_info.find("pre").contents[6]
                    total_vm_count_list = [int(s) for s in vm_val.split() if s.isdigit()]
                    if total_vm_count_list:
                        total_vm_count = total_vm_count_list[0]
                else:
                    print(item.getText())
            elif "EO" in title:
                if item.getText().startswith("EO13-A") or item.getText().startswith("EO13-B") or item.getText().startswith("EO13-C") or \
                    item.getText().startswith("EO13-D") or item.getText().startswith("EO30"):
                    project_resources=project_info.find_all('p')[2].getText().split()
                elif item.getText().startswith("EO13"):
                    project_resources=project_info.find_all('p')[4].getText().split()
                elif item.getText().startswith("EO14") or item.getText().startswith("EO15"):   
                    project_resources=project_info.find_all('p')[3].getText().split()
                elif (item.getText().startswith("EO2") and item.getText().endswith("APP")) or item.getText().startswith("EO3") or item.getText().startswith("EO4") \
                    or item.getText().startswith("EO5") or item.getText().startswith("EO6") or item.getText().startswith("EO7") or item.getText().startswith("EO8") \
                    or item.getText().startswith("EO10") or item.getText().startswith("EO16") or item.getText().startswith("EO17") or item.getText().startswith("EO25") \
                    or item.getText().startswith("EO28"):
                    project_resources=project_info.find_all('p')[1].getText().split()
                else:
                    project_resources=project_info.find_all('p')[2].getText().split()
                #print(project_resources)
                vcpu = project_resources[1]
                ram = project_resources[3]
                if (item.getText().startswith("EO1") and item.getText().endswith("stack")) or item.getText().startswith("EO11") \
                    or item.getText().startswith("EO31"):
                    volume_storage = project_resources[6]
                    total_vm_count = project_resources[8]
                elif item.getText().startswith("EO30"):
                    volume_storage = project_resources[6]
                    total_vm_count = project_resources[9]
                elif item.getText().startswith("EO3") or item.getText().startswith("EO4"): 
                    volume_storage = project_resources[5]
                    total_vm_count = project_resources[7]
                elif item.getText().startswith("EO17"):
                    volume_storage = project_resources[6]
                else:
                    volume_storage = project_resources[6]
                    total_vm_count = project_resources[9]
            else: 
                project_resources=project_info.find_all('p')[1].getText().split()
                vcpu = project_resources[1]
                ram = project_resources[3]
                volume_storage = project_resources[6]
                total_vm_count = project_resources[9]
                    
            if type(volume_storage) != int:
                if volume_storage.endswith("GB"):
                    volume_storage = volume_storage[:-2]
                if volume_storage.endswith("ex)"):
                    volume_storage = volume_storage.split("(")[0].strip()
            if type(total_vm_count) != int:
                if total_vm_count.endswith("ECFE"):
                    total_vm_count = total_vm_count[:-4]
                if total_vm_count.endswith("Volume"):
                    total_vm_count = total_vm_count[:-6]
                    
            # Node details from table
            if ("EO" in title and orderable_item_name == "CUS-EO2") or ("EO" in title and orderable_item_name == "CUS-EO18"):
                table = project_info.find_all('table')[3]
                table_rows= table.find_all('tr')
                # delete first row of the table as it the headers
                del table_rows[:1]
            elif orderable_item_name == "cENM10-B" or ( orderable_item_name.startswith("ECSON") and not (orderable_item_name.endswith("-A"))):
                table = project_info.find_all('table')[0]
                table_rows= table.find_all('tr')
                # delete first row of the table as it the headers
                del table_rows[:1]
            elif "EO" in title or ("Usage" in title and "iDUN" not in title) or ("cENM" in title and item.getText().endswith("dimensioning)")) or (item.getText().startswith("cENM5") and item.getText().endswith("IBD")) \
            or item.getText().endswith("EVNFM") or item.getText().endswith("EVNFM)") or orderable_item_name == "ECSON3-A":
                table = project_info.find_all('table')[2]
                table_rows= table.find_all('tr')
                # delete first row of the table as it the headers
                del table_rows[:1]
            else:
                table = project_info.find_all('table')[0]
                table_rows= table.find_all('tr')
                # delete first row of the table as it the headers
                del table_rows[:1]
            
            for row in table_rows:
                vm_name = row.find_all('td')[0].string
                if vm_name == None:
                    contents = row.renderContents()
                    vm_name = ''.join([i for i in row.getText() if not i.isdigit()]).strip()
                vm_name = vm_name.strip()
                if vm_name == "Director":
                    director_node_count = row.find_all('td', {"class": "confluenceTd"})[1].string.strip()
                    director_vcpu = row.find_all('td', {"class": "confluenceTd"})[2].string.strip()
                    director_ram = row.find_all('td', {"class": "confluenceTd"})[3].string.strip()
                elif vm_name == "Master":
                    master_node_count = row.find_all('td', {"class": "confluenceTd"})[1].string.strip()
                    master_vcpu = row.find_all('td', {"class": "confluenceTd"})[2].string.strip()
                    master_ram = row.find_all('td', {"class": "confluenceTd"})[3].string.strip()
                elif vm_name == "Worker" or vm_name == "Worker Application" or vm_name == "Worker pool 1" or vm_name == "Worker Pool":
                    worker_app_node_count = row.find_all('td', {"class": "confluenceTd"})[1].string.strip()
                    worker_app_vcpu = row.find_all('td', {"class": "confluenceTd"})[2].string.strip()
                    worker_app_ram = row.find_all('td', {"class": "confluenceTd"})[3].string.strip()
                elif vm_name == "Worker Network" or vm_name == "Worker Traffic" or vm_name == "worker extra" or vm_name == "Worker pool 2":
                    worker_net_node_count = row.find_all('td', {"class": "confluenceTd"})[1].string.strip()
                    worker_net_vcpu = row.find_all('td', {"class": "confluenceTd"})[2].string.strip()
                    worker_net_ram = row.find_all('td', {"class": "confluenceTd"})[3].string.strip()
                elif vm_name == "NFS server" or vm_name == "NFS (HP Flavor)" or vm_name == "NFS":
                    nfs_server_node_count = row.find_all('td', {"class": "confluenceTd"})[1].string.strip()
                    nfs_server_vcpu = row.find_all('td', {"class": "confluenceTd"})[2].string.strip()
                    nfs_server_ram = row.find_all('td', {"class": "confluenceTd"})[3].string.strip()
                elif vm_name == "Totals":
                    total_node_count = row.find_all('td', {"class": "confluenceTd"})[1].string
                    total_vcpu = row.find_all('td', {"class": "confluenceTd"})[2].string
                    total_ram = row.find_all('td', {"class": "confluenceTd"})[3].string
                elif vm_name == "cENM Client" or vm_name == "DragonflySWDP_CAS-C":
                    cENM_client_node_count = row.find_all('td', {"class": "confluenceTd"})[1].string.strip()
                    cENM_client_vcpu = row.find_all('td', {"class": "confluenceTd"})[2].string.strip()
                    cENM_client_ram = row.find_all('td', {"class": "confluenceTd"})[3].string.strip()
                else:
                    print("no matching vm name " + vm_name)
            if total_vm_count == "0" or total_vm_count == "GB":
                total_vm_count=total_node_count
            if vcpu == "0":
                vcpu = total_vcpu
            if ram == "0":
                ram = total_ram
            #EO27 has a second table with additional vm information
            '''
            if item.getText().startswith("EO27"):
                second_table = project_info.find_all('table')[1]
                table_rows= second_table.find_all('tr')
                print(table_rows)
                del table_rows[:1]
                
                for row in table_rows:
                    vm_name = row.find_all('td')[0].string
                    if vm_name == "Sentinel/Zookeeper VM":
                        nfs_server_node_count = row.find_all('td', {"class": "confluenceTd"})[1].string.strip()
                        nfs_server_vcpu = row.find_all('td', {"class": "confluenceTd"})[2].string.strip()
                        nfs_server_ram = row.find_all('td', {"class": "confluenceTd"})[3].string.strip()
                    elif vm_name == "Postgres Node VM":
                        cENM_client_node_count = row.find_all('td', {"class": "confluenceTd"})[1].string.strip()
                        cENM_client_vcpu = row.find_all('td', {"class": "confluenceTd"})[2].string.strip()
                        cENM_client_ram = row.find_all('td', {"class": "confluenceTd"})[3].string.strip()
                    else:
                        total_node_count = int(total_node_count)
                        total_vcpu = int(total_vcpu)
                        total_ram = int(total_ram)
                        total_node_count += int(row.find_all('td', {"class": "confluenceTd"})[1].string.strip())
                        total_vcpu += int(row.find_all('td', {"class": "confluenceTd"})[2].string.strip())
                        total_ram += int(row.find_all('td', {"class": "confluenceTd"})[3].string.strip())
                        total_node_count = str(total_node_count)
                        total_vcpu = str(total_vcpu)
                        total_ram = str(total_ram)
            '''
            orderable_items_info = OrderableItem(
                orderable_item_name = orderable_item_name.upper(),
                vcpu = vcpu,
                ram = ram,
                volume_storage = volume_storage,
                total_vm_count = total_vm_count,
                director_node_count = director_node_count,
                director_vcpu = director_vcpu,
                director_ram = director_ram,
                master_node_count = master_node_count,
                master_vcpu = master_vcpu,
                master_ram = master_ram,
                worker_app_node_count = worker_app_node_count,
                worker_app_vcpu = worker_app_vcpu,
                worker_app_ram = worker_app_ram,
                worker_net_node_count = worker_net_node_count,
                worker_net_vcpu = worker_net_vcpu,
                worker_net_ram = worker_net_ram,
                nfs_server_node_count = nfs_server_node_count, 
                nfs_server_vcpu = nfs_server_vcpu,
                nfs_server_ram = nfs_server_ram,
                cENM_client_node_count=cENM_client_node_count,
                cENM_client_vcpu=cENM_client_vcpu,
                cENM_client_ram=cENM_client_ram,
                total_node_count = total_node_count,
                total_vcpu = total_vcpu,
                total_ram = total_ram,
                ecfe_ip_count = 0,
                static_ip_count = 0,
                nfs_required = False,
                workers_affinity_rule = False,
                master_flavor = 0,
                master_root_volume_size = 0,
                master_root_config_volume_size = 0,
                director_flavor = 0,
                director_root_volume_size = 0,
                director_config_volume_size = 0,
                container_registry_storage_size = 0,
                worker_flavor = 0,
                worker_root_volume_size = 0)
            
            orderable_items_info.save()
            count+=1

@csrf_exempt
def cloud_calculator(request):
    cloud_name = request.POST.get('cloud_name') if request.POST.get('cloud_name') else ""
    no_of_hosts = request.POST.get('no_of_hosts') if request.POST.get('no_of_hosts') else ""
    phys_cpu = request.POST.get('phys_cpu') if request.POST.get('phys_cpu') else ""
    cpu_contention = request.POST.get('cpu_contention') if request.POST.get('cpu_contention') else ""
    phys_ram = request.POST.get('phys_ram') if request.POST.get('phys_ram') else ""
    ram_contention = request.POST.get('ram_contention') if request.POST.get('ram_contention') else ""
    projects = request.POST.get('projects') if request.POST.get('projects') else ""
    item_quantity = request.POST.getlist('item_quantity') if request.POST.get('item_quantity') else ""
    orderable_item = request.POST.getlist('item') if request.POST.get('item') else ""
    orderableItemInfo = OrderableItem.objects.filter(orderable_item_name=orderable_item).values()
    selected_cloud = request.POST.get('selected_cloud') if request.POST.get('selected_cloud') else ""
    orderable_item_expanded_name = request.POST.get('ccd_orderable_item') if request.POST.get('ccd_orderable_item') else ""
    worker_node_count = request.POST.get('worker_node_count') if request.POST.get('worker_node_count') else ""
    worker_app_vcpu = request.POST.get('worker_app_vcpu') if request.POST.get('worker_app_vcpu') else ""
    worker_app_ram = request.POST.get('worker_app_ram') if request.POST.get('worker_app_ram') else ""
    cloud_ccd_breakdown = request.POST.get('cloud_ccd_breakdown') if request.POST.get('cloud_ccd_breakdown') else ""
    expanded_orderable_item_quantity = request.POST.get('orderable_item_qty') if request.POST.get('orderable_item_qty') else ""
    modified_items = request.POST.get('modified_items_values') if request.POST.get('modified_items_values') else []
    
    if modified_items:
        modified_items = modified_items.split("},")
        for i in range(len(modified_items) - 1):
            modified_items[i] = json.loads(modified_items[i] + "}")
        modified_items[-1] = json.loads(modified_items[-1])
    if worker_node_count != "":
        last_item={
            "name": orderable_item_expanded_name,
            "node_count": worker_node_count,
            "vcpu": worker_app_vcpu,
            "ram": worker_app_ram,
            "quantity": expanded_orderable_item_quantity
        }
        if last_item["name"] == modified_items[-1]["name"]:
            modified_items[-1] = last_item
    
    if len(item_quantity) > 1 and cloud_ccd_breakdown == "":
        projects = create_project_text_from_list(item_quantity, orderable_item)
    elif selected_cloud != "":
        cloud_info = get_chosen_cloud_info(selected_cloud)
        cloud_name = selected_cloud
        no_of_hosts = cloud_info['no_of_hosts']
        phys_cpu = cloud_info['phys_cpu']
        cpu_contention =cloud_info['cpu_contention']
        phys_ram = cloud_info['phys_ram']
        ram_contention = cloud_info['ram_contention']
        if (item_quantity != "" and orderable_item != ""):
            counter = 0
            for item in orderable_item:
                cloud_ccd_breakdown += item + " x " + item_quantity[counter] + "\r\n"
                counter+=1
            get_resources_increase(item_quantity, orderable_item)
        projects = get_projects_text(cloud_ccd_breakdown, modified_items)
    elif projects == "" and len(item_quantity) == 1:
        orderableItemInfo = OrderableItem.objects.filter(orderable_item_name=orderable_item[0]).values()
        projects = create_project_text(orderable_item[0], orderableItemInfo, item_quantity[0])
    else:
        print(projects)
      
    params = {
        'cloud_name': cloud_name,
        'no_of_hosts': no_of_hosts,
        'phys_cpu': phys_cpu,
        'cpu_contention': cpu_contention,
        'phys_ram': phys_ram,
        'ram_contention': ram_contention,
        'projects': projects
        } 
    
    context = new_ccd_cloud_calculation(params)
    
    request.session['return'] = context
    
    return render(request, 'resourceaccommodator/cloud-calculator.html', context)

def create_project_text_from_list(item_quantity, orderable_item):
    orderableItemInfoList = []
    for item in orderable_item:
        print(item)
        orderableItemInfo = OrderableItem.objects.filter(orderable_item_name=item.upper()).values()
        
        if not orderableItemInfo.exists():
            continue
        for quantity in item_quantity:
            count = int(quantity)
            while count != 0:
                orderableItemInfoList.append(item.strip())
                if "0" not in [orderableItemInfo[0]['director_node_count'],orderableItemInfo[0]['director_vcpu'],orderableItemInfo[0]['director_ram']]:
                    orderableItemInfoList.append(orderableItemInfo[0]['director_node_count'])
                    orderableItemInfoList.append(orderableItemInfo[0]['director_vcpu'])
                    orderableItemInfoList.append(orderableItemInfo[0]['director_ram'])
                if "0" not in [orderableItemInfo[0]['master_node_count'],orderableItemInfo[0]['master_vcpu'],orderableItemInfo[0]['master_ram']]:
                    orderableItemInfoList.append(orderableItemInfo[0]['master_node_count'])
                    orderableItemInfoList.append(orderableItemInfo[0]['master_vcpu'])
                    orderableItemInfoList.append(orderableItemInfo[0]['master_ram'])
                if "0" not in [orderableItemInfo[0]['worker_app_node_count'],orderableItemInfo[0]['worker_app_vcpu'],orderableItemInfo[0]['worker_app_ram']]:
                    orderableItemInfoList.append(orderableItemInfo[0]['worker_app_node_count'])
                    orderableItemInfoList.append(orderableItemInfo[0]['worker_app_vcpu'])
                    orderableItemInfoList.append(orderableItemInfo[0]['worker_app_ram'])
                if "0" not in [orderableItemInfo[0]['worker_net_node_count'],orderableItemInfo[0]['worker_net_vcpu'],orderableItemInfo[0]['worker_net_ram']]:
                    orderableItemInfoList.append(orderableItemInfo[0]['worker_net_node_count'])
                    orderableItemInfoList.append(orderableItemInfo[0]['worker_net_vcpu'])
                    orderableItemInfoList.append(orderableItemInfo[0]['worker_net_ram'])
                if "0" not in [orderableItemInfo[0]['nfs_server_node_count'],orderableItemInfo[0]['nfs_server_vcpu'],orderableItemInfo[0]['nfs_server_ram']]:
                    orderableItemInfoList.append(orderableItemInfo[0]['nfs_server_node_count'])
                    orderableItemInfoList.append(orderableItemInfo[0]['nfs_server_vcpu'])
                    orderableItemInfoList.append(orderableItemInfo[0]['nfs_server_ram'])
                if "0" not in [orderableItemInfo[0]['cENM_client_node_count'],orderableItemInfo[0]['cENM_client_vcpu'],orderableItemInfo[0]['cENM_client_ram']]:
                    orderableItemInfoList.append(orderableItemInfo[0]['cENM_client_node_count'])
                    orderableItemInfoList.append(orderableItemInfo[0]['cENM_client_vcpu'])
                    orderableItemInfoList.append(orderableItemInfo[0]['cENM_client_ram'])
                    
                if orderableItemInfoList[-1] == item.strip():
                    orderableItemInfoList = orderableItemInfoList[:-1]
                count-=1
                
            item_quantity.remove(quantity)
            break

    #orderableItemInfoList = [x for x in orderableItemInfoList if str(x) != "0"]
    text_projects=""
    counter = 1
    node_name=""
    set_node_type_count=0
    if len(orderableItemInfoList) != 0:
        for value in orderableItemInfoList:
            value = value.upper()
            if value.startswith("CENM") or value.startswith("DE") or value.startswith("ECSON") or value.startswith("EO") or value.startswith("IDUN") \
               or value.startswith("PF") or value.startswith("SWDP") or value.startswith("ENIQ") or value.startswith("VROUTER") or value.startswith("MINI") \
               or value.startswith("SM") or value.startswith("TEST") or value.startswith("ORCH") or value.startswith("LITMUS") or value.startswith("STD") \
               or value.startswith("CUS") or value.startswith("GA") or value.startswith("CAPO") or value.startswith("XAAS") or value.startswith("ENM") \
               or value.startswith("CCD") or value.startswith("CD") or value.startswith("ESON") or value.startswith("GA"):
                orderable_item_name= value.upper()
                text_projects=text_projects.rsplit('\r\n',1)[0]
                set_node_type_count=0
                node_type = set_node_type(set_node_type_count)
                text_projects+="\r\n"+value + "-" + node_type + str(counter) + "," 
            else:
                if (counter % 3) == 0:
                    text_projects+=value + "\r\n"
                    set_node_type_count+=1
                    node_type = set_node_type(set_node_type_count)
                    text_projects+=orderable_item_name + "-" + node_type + str(counter) + ","
                else:
                    text_projects+=value + ","
                counter+=1      
    
    text_projects=text_projects.rsplit('\n',1)[0]
    #print(text_projects)
    return text_projects.strip()

def create_project_text(orderable_item, orderableItemInfo, item_quantity):
    orderableItemInfoList = []
    if "0" not in [orderableItemInfo[0]['director_node_count'],orderableItemInfo[0]['director_vcpu'],orderableItemInfo[0]['director_ram']]:
        orderableItemInfoList.append(orderableItemInfo[0]['director_node_count'])
        orderableItemInfoList.append(orderableItemInfo[0]['director_vcpu'])
        orderableItemInfoList.append(orderableItemInfo[0]['director_ram'])
    if "0" not in [orderableItemInfo[0]['master_node_count'],orderableItemInfo[0]['master_vcpu'],orderableItemInfo[0]['master_ram']]:
        orderableItemInfoList.append(orderableItemInfo[0]['master_node_count'])
        orderableItemInfoList.append(orderableItemInfo[0]['master_vcpu'])
        orderableItemInfoList.append(orderableItemInfo[0]['master_ram'])
    if "0" not in [orderableItemInfo[0]['worker_app_node_count'],orderableItemInfo[0]['worker_app_vcpu'],orderableItemInfo[0]['worker_app_ram']]:
        orderableItemInfoList.append(orderableItemInfo[0]['worker_app_node_count'])
        orderableItemInfoList.append(orderableItemInfo[0]['worker_app_vcpu'])
        orderableItemInfoList.append(orderableItemInfo[0]['worker_app_ram'])
    if "0" not in [orderableItemInfo[0]['worker_net_node_count'],orderableItemInfo[0]['worker_net_vcpu'],orderableItemInfo[0]['worker_net_ram']]:
        orderableItemInfoList.append(orderableItemInfo[0]['worker_net_node_count'])
        orderableItemInfoList.append(orderableItemInfo[0]['worker_net_vcpu'])
        orderableItemInfoList.append(orderableItemInfo[0]['worker_net_ram'])
    if "0" not in [orderableItemInfo[0]['nfs_server_node_count'],orderableItemInfo[0]['nfs_server_vcpu'],orderableItemInfo[0]['nfs_server_ram']]:
        orderableItemInfoList.append(orderableItemInfo[0]['nfs_server_node_count'])
        orderableItemInfoList.append(orderableItemInfo[0]['nfs_server_vcpu'])
        orderableItemInfoList.append(orderableItemInfo[0]['nfs_server_ram'])
    if "0" not in [orderableItemInfo[0]['cENM_client_node_count'],orderableItemInfo[0]['cENM_client_vcpu'],orderableItemInfo[0]['cENM_client_ram']]:
        orderableItemInfoList.append(orderableItemInfo[0]['cENM_client_node_count'])
        orderableItemInfoList.append(orderableItemInfo[0]['cENM_client_vcpu'])
        orderableItemInfoList.append(orderableItemInfo[0]['cENM_client_ram'])
    
    #orderableItemInfoList = [x for x in orderableItemInfoList if str(x) != "0"]
    
    if len(orderableItemInfoList) != 0:
        text_projects=str(orderable_item) + "-node,"
        item_quantity=int(item_quantity)
        while item_quantity != 0:
            counter=1
            for val in orderableItemInfoList:
                if (counter % 3) == 0: 
                    text_projects+=str(val) + "\r\n" + str(orderable_item) + "-node" + str(item_quantity) + str(counter) + ","
                else:
                    text_projects+=str(val) + ","
                counter+=1
            item_quantity-=1
        text_projects=text_projects.rsplit('\n',1)[0]
        return text_projects
    else:
        return ""

@csrf_exempt 
def new_ccd_cloud_calculation(param_list): 
    global vcpu_increase
    global ram_increase
    cloud_name = str(param_list['cloud_name']) 
    no_of_hosts = int(param_list['no_of_hosts']) 
    phys_cpu = int(param_list['phys_cpu']) 
    cpu_contention = float(param_list['cpu_contention']) 
    phys_ram = int(param_list['phys_ram']) 
    ram_contention = float(param_list['ram_contention']) 
    projects = str(param_list['projects']) 
     
    hosts = OrderedDict() 
    cpu = int(phys_cpu * cpu_contention) 
    ram = int(phys_ram * ram_contention) 
    for i in range(0,no_of_hosts): 
        hosts[cloud_name+"-compute-"+str(i)]={'cpu': cpu, 'ram': ram, 'instances': [], 'projects': []} 
     
    host_map = [] 
    vm_map = [] 
    all_vms = {} 
    vms = OrderedDict() 
    mapping = [] 
    
    for project in projects.split('\r\n'): 
        if project != "" and project != "\r\n":
            data = project.split(",")
            project_name = data[0] 
            no_of_vms = int(data[1]) 
            vm_cpu = int(data[2]) 
            vm_ram = int(data[3]) 
            #print("Project Name: " + str(project_name) + " No of vm's: " + str(no_of_vms) + " CPU: " + str(vm_cpu) + " RAM: " + str(vm_ram))
         
            for i in range(0,no_of_vms):
                p = project_name + "-" + str(i)
                vms[p] = {"cpu": vm_cpu, "ram": vm_ram, "project_name": project_name}
                all_vms.update({p: {"cpu": vm_cpu, "ram": vm_ram, "project_name": project_name}})
        #print(all_vms)    
             
    for vm in vms: 
        for host in hosts: 
            if host in host_map: 
                continue 
            if vms[vm]['project_name'] in hosts[host]['projects']: 
                continue 
            if vm in vm_map: 
                continue 
            else: 
                if hosts[host]["cpu"] - vms[vm]["cpu"] > 0 and hosts[host]["ram"] - vms[vm]["ram"] > 0: 
                    hosts[host]["cpu"] = hosts[host]["cpu"] - vms[vm]["cpu"] 
                    hosts[host]["ram"] = hosts[host]["ram"] - vms[vm]["ram"] 
                    hosts[host]["instances"].append(vm) 
                    hosts[host]["projects"].append(vms[vm]["project_name"]) 
                    host_map.append(host) 
                    vm_map.append(vm) 
                    mapping.append((host,vm)) 
            if len(host_map) == len(hosts): 
                    host_map = []   
     
    remaining_cpu = 0 
    remaining_ram = 0 
    no_instances = 0 
    for host in hosts: 
        remaining_cpu += hosts[host]["cpu"] 
        remaining_ram += hosts[host]["ram"] 
        no_instances += len(hosts[host]["instances"]) 
     
    skipped_vms = {} 
    for vm in all_vms: 
        if vm not in vm_map: 
            skipped_vms.update({vm: all_vms[vm]}) 
           
    cloud_plan_text_file_name = "cloud_plan.txt"
    with open(cloud_plan_text_file_name, "w") as text_file:
        text_file.write(projects) 
    file = open(cloud_plan_text_file_name, 'r')
    cloud_plan_contents = file.read()
    file.close()
    cwd = os.getcwd()
    try:
        os.remove(cwd + '/' + cloud_plan_text_file_name)
    except OSError:
        pass

    
    total_remaining_cpu=round(float(remaining_cpu)/(cpu*no_of_hosts)*100,1)
    
    cpu_increased_by=vcpu_increase
    
    total_remaining_ram=round(float(remaining_ram)/(ram*no_of_hosts)*100,1)
   
    av_remaining_cpu_per_host = round((remaining_cpu/len(hosts)/float(cpu))*100,1)
    av_remaining_ram_per_host = round((remaining_ram/len(hosts)/float(ram))*100,1)
 
    response = { 
        "result": "True", 
        "cloud_name": cloud_name, 
        "hosts": hosts, 
        "cloud_summary": {
            
            "remaining_cpu": str(remaining_cpu),
            "cpu_no_of_hosts": str(cpu*no_of_hosts),
            "total_remaining_cpu": total_remaining_cpu,
            "cpu_increased_by": str(vcpu_increase),
            "remaining_ram": str(int(remaining_ram)),
            "ram_no_of_hosts": str(int(ram*no_of_hosts)),
            "total_remaining_ram": total_remaining_ram,
            "ram_increase": str(ram_increase),
            "remaining_cpu_len_hosts": str(round(remaining_cpu/len(hosts))),
            "av_remaining_cpu_per_host":av_remaining_cpu_per_host,
            "remaining_ram_len_hosts":str(int(remaining_ram/len(hosts))),
            "av_remaining_ram_per_host": av_remaining_ram_per_host,
            "total_number_of_instances": no_instances,
            
            },
        "cloud_plan_text": cloud_plan_contents   
        } 
    if skipped_vms != {}: 
        response.update({"skipped_vms": skipped_vms}) 
    
    #logger.info("New CCD Cloud Calculator successfully run.") 
    return response 

def get_chosen_cloud_info(selected_cloud):
    cloud_info = get_cloud_info(selected_cloud)
    host_count = cloud_info['hosts_count']
    total_cloud_cpu = cloud_info['total_cpu']
    cpu_contention = cloud_info['cpu_ratio']
    total_cloud_ram = cloud_info['total_ram']
    ram_contention = cloud_info['ram_ratio']
    phys_cpu_per_host = int(int(total_cloud_cpu)/int(host_count))
    phys_ram_per_host = int((int(total_cloud_ram)/int(host_count))/1024)
    selected_cloud_dict = {}
    selected_cloud_dict['no_of_hosts'] = cloud_info['hosts_count']
    selected_cloud_dict['phys_cpu'] = phys_cpu_per_host
    selected_cloud_dict['cpu_contention'] = cpu_contention
    selected_cloud_dict['phys_ram'] = phys_ram_per_host
    selected_cloud_dict['ram_contention'] = ram_contention
    return selected_cloud_dict

def get_orderable_item_api(request):
    orderable_item_name = request.GET.get('orderable_item')
    if(OrderableItem.objects.filter(orderable_item_name=orderable_item_name.upper())):
        orderable_item_info = list(OrderableItem.objects.filter(orderable_item_name=orderable_item_name.upper()).values())[0]
    else:
        orderable_item_info = {'worker_app_node_count': '0', 'worker_app_vcpu': '0', 'worker_app_ram': '0'}
    
    return JsonResponse({"orderable_item_info": orderable_item_info}, safe=False)

def get_all_orderable_items_api(request):
    orderable_items = OrderableItem.objects.all()

    orderable_items_info= [vars(item) for item in orderable_items]

    for item in orderable_items_info:
        del item['_state']

    return JsonResponse({"number_of_orderable_items": len(orderable_items_info),
                         "orderable_items_info": orderable_items_info}, safe=False)
    
def get_all_orderable_items_dtt_api(request):
    orderable_items = list(OrderableItem.objects.filter(self_managed=False).values('orderable_item_name','vcpu', 'ram', 'volume_storage'))
    
    orderable_item_deployment_types = ["cENM","EO","DE-CCD","ECSON","ENIQ","IDUN","SWDP"]
    for orderable_item in orderable_items:
        orderable_item["type"] = "CCD"
        for deployment_type in orderable_item_deployment_types:
            if deployment_type.upper() in orderable_item["orderable_item_name"].upper():
                orderable_item["deploymentType"] = deployment_type
                break
        if "deploymentType" not in orderable_item:
            orderable_item["deploymentType"] = "Other"
    
    return JsonResponse(orderable_items, safe=False)

def get_projects_text(cloud_ccd_breakdown, modified_items):
    #Take the line out of cloud_ccd_breakdown for the orderable item being expanded and run the create_projects_from_list_file
    #Then add the orderable_item with the new_info to that file and run calculator
    modified_items_names = [d["name"] for d in modified_items]
    text_with_expansion=""
    orderable_item_names = []
    orderable_items_quantities = []
    self_managed_names = OrderableItem.objects.filter(self_managed=True).values_list('orderable_item_name', flat=True)
    for line in cloud_ccd_breakdown.splitlines():
        orderable_item_name = line.split(" ")[0]
        orderable_item_qty = line.split(" ")[2]
        hyphen_count = orderable_item_name.count("-")
        if(orderable_item_name in modified_items_names):
            current_item = modified_items[modified_items_names.index(orderable_item_name)]
            expansion_orderable_item_quantity = orderable_item_qty
            # This is reached if only a select number of the orderable items are due to be expanded
            if int(expansion_orderable_item_quantity) != int(current_item["quantity"]):
                quantity_orderable_item_not_being_expanded = int(expansion_orderable_item_quantity) - int(current_item["quantity"])
                orderable_item_names.append(orderable_item_name)
                orderable_items_quantities.append(quantity_orderable_item_not_being_expanded)

            text_with_expansion += add_expansion_info_to_project_file(current_item["name"],
                                                                     current_item["quantity"],
                                                                     current_item["node_count"], current_item["vcpu"], current_item["ram"]) + "\r\n"
        elif(orderable_item_name in self_managed_names):
            orderable_item_names.append(orderable_item_name)
            orderable_items_quantities.append(orderable_item_qty)
        elif(orderable_item_name.startswith("ga_") or orderable_item_name.startswith("GA_")):
            orderable_item_name = (orderable_item_name.split("_")[0] + "-" + orderable_item_name.split("_")[1])
            orderable_item_names.append(orderable_item_name)
            orderable_items_quantities.append(orderable_item_qty)
        elif(hyphen_count==1):
            orderable_item_name = (orderable_item_name.split("-")[0] + "-" + orderable_item_name.split("-")[1])
            orderable_item_names.append(orderable_item_name)
            orderable_items_quantities.append(orderable_item_qty)
        elif(hyphen_count==2):
            orderable_item_name = (orderable_item_name.split("-")[0] + "-" + orderable_item_name.split("-")[1] + "-" + orderable_item_name.split("-")[2])
            orderable_item_names.append(orderable_item_name)
            orderable_items_quantities.append(orderable_item_qty)
        elif(hyphen_count==3):
            orderable_item_name = (orderable_item_name.split("-")[0] + "-" + orderable_item_name.split("-")[1] + "-" + orderable_item_name.split("-")[2] + "-" + orderable_item_name.split("-")[3])
            orderable_item_names.append(orderable_item_name)
            orderable_items_quantities.append(orderable_item_qty)
        elif("-" in orderable_item_name):
            orderable_item_name = orderable_item_name.split("-")[0]
            orderable_item_names.append(orderable_item_name)
            orderable_items_quantities.append(orderable_item_qty)
        elif("_" in orderable_item_name):
            orderable_item_name = orderable_item_name.split("_")[0]
            orderable_item_names.append(orderable_item_name)
            orderable_items_quantities.append(orderable_item_qty)
        else:#orderable_item_name not in modified_items_names and doesn't have '-' or '_' in the name
            orderable_item_names.append(orderable_item_name)
            orderable_items_quantities.append(orderable_item_qty)
    if modified_items == "":
        text_projects = create_project_text_from_list(orderable_items_quantities, orderable_item_names)
    else:
        text_without_expansion = create_project_text_from_list(orderable_items_quantities, orderable_item_names)
        text_projects = text_without_expansion + "\r\n" + text_with_expansion
    return text_projects
    
def add_expansion_info_to_project_file(orderable_item_expanded_name, expansion_orderable_item_quantity, worker_node_count, worker_app_vcpu, worker_app_ram):
    orderableItemInfo = OrderableItem.objects.filter(orderable_item_name=orderable_item_expanded_name.upper()).values()
    orderableItemInfoList = []
    orderableItemInfoList.append(orderableItemInfo[0]['director_node_count'])
    orderableItemInfoList.append(orderableItemInfo[0]['director_vcpu'])
    orderableItemInfoList.append(orderableItemInfo[0]['director_ram'])
    orderableItemInfoList.append(orderableItemInfo[0]['master_node_count'])
    orderableItemInfoList.append(orderableItemInfo[0]['master_vcpu'])
    orderableItemInfoList.append(orderableItemInfo[0]['master_ram'])
    orderableItemInfoList.append(worker_node_count)
    orderableItemInfoList.append(worker_app_vcpu)
    orderableItemInfoList.append(worker_app_ram)
    orderableItemInfoList.append(orderableItemInfo[0]['worker_net_node_count'])
    orderableItemInfoList.append(orderableItemInfo[0]['worker_net_vcpu'])
    orderableItemInfoList.append(orderableItemInfo[0]['worker_net_ram'])
    orderableItemInfoList.append(orderableItemInfo[0]['nfs_server_node_count'])
    orderableItemInfoList.append(orderableItemInfo[0]['nfs_server_vcpu'])
    orderableItemInfoList.append(orderableItemInfo[0]['nfs_server_ram'])
    orderableItemInfoList.append(orderableItemInfo[0]['cENM_client_node_count'])
    orderableItemInfoList.append(orderableItemInfo[0]['cENM_client_vcpu'])
    orderableItemInfoList.append(orderableItemInfo[0]['cENM_client_ram'])
    
    calculate_resources_increase(orderableItemInfo, expansion_orderable_item_quantity, worker_node_count, worker_app_vcpu, worker_app_ram)

    orderableItemInfoList = [x for x in orderableItemInfoList if str(x) != "0"]
    text_projects=""
    item_quantity=int(expansion_orderable_item_quantity)
    while item_quantity != 0:
        counter=1
        set_node_type_count=0
        for val in orderableItemInfoList:
            if (counter==1):
                text_projects+=str(orderable_item_expanded_name) + "-EXP-director" + str(item_quantity) + "," + str(val) + ","
                set_node_type_count+=1
            elif(counter % 3) == 0:
                text_projects+=str(val) + "\r\n" + str(orderable_item_expanded_name) + "-EXP-"
                node = set_node_type(set_node_type_count)
                text_projects+= node + str(item_quantity) + ","
                set_node_type_count+=1
            else:
                text_projects+=str(val) + ","
            counter+=1
        item_quantity-=1
        text_projects=text_projects.rsplit(str(orderable_item_expanded_name),1)[0]
    text_projects=text_projects.rsplit('\n',1)[0]
    return text_projects.strip()
    
def set_node_type(number):
    switcher={
           0:'director',
           1:'master',
           2:'worker_app',
           3:'worker_net',
           4:'nfs_server',
           5:'cenm_client'
    }
    return switcher.get(number, "Node type missing")

def calculate_resources_increase(orderableItemInfo, expansion_orderable_item_quantity, worker_node_count, worker_app_vcpu, worker_app_ram):
    global vcpu_increase
    global ram_increase
    node_count_before_expansion = int(orderableItemInfo[0]['worker_app_node_count'])
    vcpu_before_expansion = int(orderableItemInfo[0]['worker_app_vcpu'])
    ram_before_expansion = int(orderableItemInfo[0]['worker_app_ram'])
    worker_diff = int(worker_node_count) - int(node_count_before_expansion)
    vcpu_diff = int(worker_app_vcpu) - int(vcpu_before_expansion)
    ram_diff = int(worker_app_ram) - int(ram_before_expansion)
    if(worker_diff == 0):
        vcpu_increase = int(node_count_before_expansion) * vcpu_diff
        ram_increase = int(node_count_before_expansion) * ram_diff
    elif (ram_diff == 0 and vcpu_diff == 0):
        vcpu_increase = worker_diff * int(vcpu_before_expansion)
        ram_increase = worker_diff * int(ram_before_expansion)
    elif (worker_diff != 0):
        vcpu_increase = (int(node_count_before_expansion) * vcpu_diff) + (worker_diff * int(worker_app_vcpu))
        ram_increase = (int(node_count_before_expansion) * ram_diff) + (worker_diff * int(worker_app_ram))
    
    vcpu_increase = vcpu_increase * int(expansion_orderable_item_quantity)
    ram_increase = ram_increase * int(expansion_orderable_item_quantity)
    
def get_resources_increase(item_quantity, orderable_item):
    text = create_project_text_from_list(item_quantity, orderable_item)
    global vcpu_increase
    global ram_increase
    for line in text.splitlines():
        vcpu_increase += int(line.split(",")[1]) * int(line.split(",")[2])
        ram_increase += int(line.split(",")[1]) * int(line.split(",")[3])

@csrf_exempt
def test(request):
    orderable_item_expanded_name = request.POST.get('ccd_orderable_item') if request.POST.get(
        'ccd_orderable_item') else ""
    worker_node_count = request.POST.get('worker_node_count') if request.POST.get('worker_node_count') else ""
    worker_app_vcpu = request.POST.get('worker_app_vcpu') if request.POST.get('worker_app_vcpu') else ""
    worker_app_ram = request.POST.get('worker_app_ram') if request.POST.get('worker_app_ram') else ""
    expanded_orderable_item_quantity = request.POST.get('orderable_item_qty') if request.POST.get(
        'orderable_item_qty') else ""
    modified_items = request.POST.get('modified_items_values') if request.POST.get('modified_items_values') else []

    if modified_items:
        modified_items=modified_items.split("},")
        for i in range(len(modified_items) - 1):
            modified_items[i] = json.loads(modified_items[i] + "}")
        modified_items[-1] = json.loads(modified_items[-1])
    if worker_node_count != "":
        modified_items.append({
            "name": orderable_item_expanded_name,
            "node_count": worker_node_count,
            "vcpu": worker_app_vcpu,
            "ram": worker_app_ram,
            "quantity": expanded_orderable_item_quantity
        })
    return JsonResponse(modified_items,safe=False)

@csrf_exempt
def get_sm_orderable_item():
    self_managed_ccd_details = get_self_managed_ccd_data()
    
    for deployment,details in self_managed_ccd_details.items():
        if len(OrderableItem.objects.filter(orderable_item_name=deployment.upper().replace("_", "-"))) > 0:
            if details["total_node_count"] == 0:
                continue
        orderable_items_info = OrderableItem(
            orderable_item_name = deployment.upper().replace("_", "-"),
            self_managed = True,
            vcpu = details["total_vcpus"],
            ram = details["total_ram"],
            volume_storage = details["total_cinder_storage"],
            total_vm_count = details["total_node_count"],
            director_node_count = details["director_node_count"],
            director_vcpu = details["flavors"]["director"][details["flavors"]["director"]["flavor_names"][0]]["vcpus"] if len(details["flavors"]["director"]["flavor_names"]) > 0 else 0,
            director_ram = details["flavors"]["director"][details["flavors"]["director"]["flavor_names"][0]]["ram"] if len(details["flavors"]["director"]["flavor_names"]) > 0 else 0,
            master_node_count = details["master_node_count"],
            master_vcpu = details["flavors"]["master"][details["flavors"]["master"]["flavor_names"][0]]["vcpus"] if len(details["flavors"]["master"]["flavor_names"]) > 0 else 0,
            master_ram = details["flavors"]["master"][details["flavors"]["master"]["flavor_names"][0]]["ram"] if len(details["flavors"]["master"]["flavor_names"]) > 0 else 0,
            worker_app_node_count = details["worker_node_count"] if len(details["flavors"]["worker"])<2 else details["flavors"]["worker"][details["flavors"]["worker"]["flavor_names"][0]]["count"],
            worker_app_vcpu = details["flavors"]["worker"][details["flavors"]["worker"]["flavor_names"][0]]["vcpus"] if len(details["flavors"]["worker"]["flavor_names"]) > 0 else 0,
            worker_app_ram = details["flavors"]["worker"][details["flavors"]["worker"]["flavor_names"][0]]["ram"] if len(details["flavors"]["worker"]["flavor_names"]) > 0 else 0,
            worker_net_node_count = 0 if len(details["flavors"]["worker"]["flavor_names"])<2 else details["flavors"]["worker"][details["flavors"]["worker"]["flavor_names"][1]]["count"],
            worker_net_vcpu = 0 if len(details["flavors"]["worker"]["flavor_names"])<2 else details["flavors"]["worker"][details["flavors"]["worker"]["flavor_names"][1]]["vcpus"],
            worker_net_ram = 0 if len(details["flavors"]["worker"]["flavor_names"])<2 else details["flavors"]["worker"][details["flavors"]["worker"]["flavor_names"][1]]["ram"],
            nfs_server_node_count = 0, 
            nfs_server_vcpu = 0,
            nfs_server_ram = 0,
            cENM_client_node_count=0,
            cENM_client_vcpu=0,
            cENM_client_ram=0,
            total_node_count = details["total_node_count"],
            total_vcpu = details["total_vcpus"],
            total_ram = details["total_ram"],
            ecfe_ip_count = 0,
            static_ip_count = 0,
            nfs_required = False,
            workers_affinity_rule = False)
        orderable_items_info.save()
    
    return "done"