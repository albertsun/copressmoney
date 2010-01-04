from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.shortcuts import render_to_response

def home(request):
    s = "copressmoney - /views.py home"
    #t = get_template('index.html')
    #s = t.render(Context({'message':s}))
    #return HttpResponse(s)
    return render_to_response('index.html', {'message':s})
    #return render_to_response('index.html', locals())
