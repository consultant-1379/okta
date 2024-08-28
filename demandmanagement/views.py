from __future__ import unicode_literals
from django.shortcuts import render,get_object_or_404
import requests
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from io import BytesIO
from xlsxwriter import Workbook
from xlsxwriter import exceptions as xlxExceptions
from django.contrib.auth.decorators import login_required

JIRA_API_URL="https://eteamproject.internal.ericsson.com/rest/api/2/search?jql="
username = "protoadm10"
password = "vFc214db8TycS6522"
    
@login_required(login_url='/')
def demand_management(request):
    return render(request, "demandmanagement/demandmanagement.html", sort_requests("all"))

def demand_management_api(request):
    return JsonResponse(sort_requests("all"))

def sort_requests(pdg_area):
    all_dm_tickets = sorted(get_demand_management_requests(), key = lambda k: k["fields"]["created"])
    area_count = {}
    timebox_expired = []
    expansion_requests = []
    other_requests = []
    approved_requests = []
    now = datetime.now()
    
    for ticket in all_dm_tickets:
        if ticket["fields"]["status"]["name"].lower() not in ["template","resolved"]:
            ticket["fields"]["pdg_area"] = ticket["fields"]["customfield_16801"]
            if pdg_area != "all" and ticket["fields"]["pdg_area"]["value"] != pdg_area:
                continue
            ticket["fields"]["timebox"] = ""
            ticket["fields"]["timebox"] = ticket["fields"]["customfield_26300"]
            ticket["fields"]["team"] = ticket["fields"]["customfield_15706"]
            ticket["fields"]["created"] = ticket["fields"]["created"].split('T')[0]
            ticket["fields"]["transitionDate"] = ""
            del ticket["fields"]["customfield_16801"]
            del ticket["fields"]["customfield_26300"]
            
            if ticket["fields"]["comment"]["comments"]:
                ticket["fields"]["lastComment"] = ticket["fields"]["comment"]["comments"][-1]["body"]
                ticket["fields"]["lastCommenter"] = ticket["fields"]["comment"]["comments"][-1]["author"]["displayName"]
            else:
                ticket["fields"]["lastComment"] = ""
            
            req_area = ticket["fields"]["pdg_area"]["value"]
            area_count[req_area] = 1 if req_area not in area_count else area_count[req_area] + 1
            
            if ticket["fields"]["timebox"]:
                timebox = datetime.strptime(ticket["fields"]["timebox"], '%Y-%m-%d')
                if timebox <= now + timedelta(days=14):
                    timebox_expired.append(ticket)
                    continue
            else:
                ticket["fields"]["timebox"] = ""
            
            #created = datetime.strptime(ticket["fields"]["created"], '%Y-%m-%d')
            #if created > now - timedelta(days=7):
            #    new_requests.append(ticket)
            #    continue
            
            if ticket["fields"]["status"]["name"].lower() in ["approved"]:
                for transition in reversed(ticket["changelog"]["histories"]):
                #transition = ticket["changelog"]["histories"][-1]
                    if transition["items"][0]["toString"] and transition["items"][0]["toString"].lower() in ["approved"]:
                        #transition_date_string = transition["created"].split('T')[0]
                        #transition_date = datetime.strptime(transition_date_string, '%Y-%m-%d')
                        #if transition_date > now - timedelta(days=30):
                        ticket["fields"]["transitionDate"] = transition["created"].split('T')[0] #transition_date
                        break
                approved_requests.append(ticket)
                continue
            
            if "expansion" in ticket["fields"]["summary"].lower():
                expansion_requests.append(ticket)
            else:
                other_requests.append(ticket)
        
    
    context = {
        'area_count': area_count,
        'dm_requests': {
            'approved': {
                    "title": 'Approved Requests',
                    "requests": approved_requests,
                    "count": len(approved_requests),
                    "extra_columns": True
                },
            'timebox_expired': {
                    "title": 'Timebox Expired/Expiring',
                    "requests": timebox_expired,
                    "count": len(timebox_expired),
                    "extra_columns": False
                },
            'expansions': {
                    "title": 'Expansions',
                    "requests": expansion_requests,
                    "count": len(expansion_requests),
                    "extra_columns": False
                },
            'other': {
                    "title": 'All Other Requests',
                    "requests": other_requests,
                    "count": len(other_requests),
                    "extra_columns": False
                }
            }
        }
    return context

def get_demand_management_requests():
    jira_demand_management_api = "project=CIS AND component=\"ITTE Demand Management Openstack Request\"  AND component=\"Openstack_TEaaS\" AND status!=\"Closed\" &startAt=0&maxResults=2000&fields=status,description,summary,reporter,customfield_16801,created,customfield_26300,customfield_15706,comment&expand=changelog"
    session = requests.Session()
    session.auth = (username, password)
    response = session.get(JIRA_API_URL+jira_demand_management_api)
    jira_info = response.json()
    return jira_info["issues"]

def generate_demand_management_report(request):
    pdg_area = request.GET.get('pdgs')
    HEADINGS_LIST = ['JIRA','Summary','Status','Transition Date','Reporter','Team','PDG/Area','Created','Timebox']
    response, book, output = get_excel_workbook_info()
    sorted_requests = sort_requests(pdg_area)
    
    for request_type,data in sorted_requests["dm_requests"].items():
        sheet = book.add_worksheet(request_type.upper()) 
        sheet.merge_range('A1:B1', "Total Requests: " + str(data["count"]), book.add_format({'bold': 1}))
        for i in range(0, len(HEADINGS_LIST)):
            sheet.write(2, i, HEADINGS_LIST[i], book.add_format({'bold': 1}))
            index = 3
            for request in data["requests"]:
                temp_list = [request["key"], request["fields"]["summary"], request["fields"]["status"]["name"], request["fields"]["transitionDate"], 
                             request["fields"]["reporter"]["displayName"], request["fields"]["team"], request["fields"]["pdg_area"]["value"],
                             request["fields"]["created"], request["fields"]["timebox"]]
        
                for j in range(len(HEADINGS_LIST)):
                    sheet.set_column(index, j, 15)
                    sheet.write(index, j, temp_list[j])
                index = index + 1
        
    book.close()
    response.write(output.getvalue())
    return response
    
def get_excel_workbook_info():
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    output = BytesIO()
    book = Workbook(output,{'in_memory': True})
    response['Content-Disposition'] = "attachment; filename=demand-management-report.xlsx"
    return response, book, output

