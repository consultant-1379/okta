from __future__ import unicode_literals
import requests

METEO_URL="https://meteo.athtem.eei.ericsson.se/typhoon"

def get_clouds_info():
    meteo_clouds_info_api = "/get-clouds-info-api"
    session = requests.Session()
    response = session.get(METEO_URL+meteo_clouds_info_api)
    clouds_info = response.json()
    return sorted(clouds_info["clouds"], key=lambda k: k['cloud_name'])
    
def get_projects_info():
    meteo_projects_info_api = "/get-project-list-api"
    session = requests.Session()
    response = session.get(METEO_URL+meteo_projects_info_api)
    projects_info = response.json()
    return projects_info

def get_projects_breakdown_info():
    meteo_projects_breakdown_api = "/get-project-type-breakdown-api"
    session = requests.Session()
    response = session.get(METEO_URL+meteo_projects_breakdown_api)
    projects_breakdown_info = response.json()
    return projects_breakdown_info

def get_ccd_projects_info():
    meteo_ccd_projects_info_api = "/get-ccd-project-list-api"
    session = requests.Session()
    response = session.get(METEO_URL+meteo_ccd_projects_info_api)
    ccd_projects_info = response.json()
    return ccd_projects_info

def get_cloud_info(selected_cloud):
    meteo_cloud_info_api = "/get-cloud-info-api/?cloud_name=" + selected_cloud
    session = requests.Session()
    response = session.get(METEO_URL + meteo_cloud_info_api)
    cloud_info = response.json()
    return cloud_info

def get_resource_allocation_by_program():
    meteo_program_allocation_api = "/get-resource-allocation-by-program/"
    session = requests.Session()
    response = session.get(METEO_URL + meteo_program_allocation_api)
    program_allocation_info = response.json()
    return program_allocation_info

def get_returned_projects(days):
    meteo_returned_projects_api = "/get-projects-returned/?days="+str(days)
    session = requests.Session()
    response = session.get(METEO_URL + meteo_returned_projects_api)
    returned_projects_info = response.json()
    return returned_projects_info

def get_cloud_capacity_data():
    meteo_cloud_capacity_data_api = "/get-cloud-capacity-status-data-api"
    session = requests.Session()
    response = session.get(METEO_URL + meteo_cloud_capacity_data_api)
    cloud_capacity_data = response.json()
    return cloud_capacity_data

def get_self_managed_ccd_data():
    meteo_self_managed_orderable_item_data_api = "/get-self-managed-orderable-item-data"
    session = requests.Session()
    response = session.get(METEO_URL + meteo_self_managed_orderable_item_data_api)
    self_managed_orderable_item_data = response.json()
    return self_managed_orderable_item_data

def get_all_deployment_type_resources():
    meteo_deployment_types_resources_api = "/get-all-deployment-resources-api/"
    session = requests.Session()
    response = session.get(METEO_URL + meteo_deployment_types_resources_api)
    all_deployment_type_resources = response.json()
    return all_deployment_type_resources