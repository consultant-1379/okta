from __future__ import unicode_literals
from django.shortcuts import render,get_object_or_404
import requests
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from io import BytesIO
from xlsxwriter import Workbook
from xlsxwriter import exceptions as xlxExceptions
from django.contrib.auth.decorators import login_required

DTT_FORECASTS_API_URL="https://atvdtt.athtem.eei.ericsson.se/api/forecasts"
username = "protoadm10"
password = "vFc214db8TycS6522"
    
@login_required(login_url='/')
def forecasts(request):
    return render(request, "forecasts/forecasts.html", sort_requests())

def forecasts_api(request):
    return JsonResponse(sort_requests("all"))

def get_forecasts():
    session = requests.Session()
    session.auth = (username, password)
    response = session.get(DTT_FORECASTS_API_URL)
    forecast_info = response.json()
    return forecast_info


def sort_requests():
    all_forecasts = get_forecasts()
    
    openstack_forecasts = []
    for group in all_forecasts:
        for forecast in group["rows"]:
            if forecast["teType"] in ["vENM","CCD"]:
                forecast["forecast"] = group["name"]
                forecast["year"] = group["year"]
                openstack_forecasts.append(forecast)
    
    
    context = {
        'forecasts_list': openstack_forecasts
        }
    
    print(context)
    return context

def generate_forecast_report(request):
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
    response['Content-Disposition'] = "attachment; filename=forecast-report.xlsx"
    return response, book, output

