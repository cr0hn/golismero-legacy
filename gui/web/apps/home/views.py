#!/usr/bin/python
# -*- coding: utf-8 -*-


from django.template import RequestContext
from django.shortcuts import render_to_response, redirect

def home(request):
    return render_to_response('index.html', context_instance=RequestContext(request))
	
def login(request):
    return render_to_response('login.html', context_instance=RequestContext(request))
	
def master(request):
    return render_to_response('master.html', context_instance=RequestContext(request))

