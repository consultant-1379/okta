from __future__ import unicode_literals
from django.shortcuts import render,redirect,get_object_or_404
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.views.generic import ListView
from taggit.models import Tag
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import auth
from django.contrib.auth import authenticate,login
import copy
import json, copy, datetime

# Create your views here.
@csrf_exempt
def login(request):
    next = request.GET.get('next')
    if next is not None:
        context = {"next" : next}
    else:
        context = {"next" : "utils/success/"}
    return render(request,'utils/login.html', context)

@csrf_exempt
def user_auth(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    next = request.POST.get('next', '')
    if next in [ None, ""]:
        next = "utils/success/"
    user = auth.authenticate(request, username=username, password=password)
    context = {}
    #context['username'] = username
    if user is not None:
        auth.login(request, user)
        return redirect(next)
    else:
        # stay on login page so user can re-try
        context["result"] = "Your username/password appears to be invalid. Please try again"
        return render(request, "utils/login.html", context)

@csrf_exempt
def logout(request):
    auth.logout(request)
    next = request.POST.get('next', '')
    if next in [ None, ""]:
        next = "/"
    return redirect(next)

@csrf_exempt
def success(request):
    return render(request, "utils/success.html")

