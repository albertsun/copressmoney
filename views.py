from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.shortcuts import render_to_response

from ledger.models import *

def home(request):
    s = "copressmoney - /views.py home"
    #t = get_template('index.html')
    #s = t.render(Context({'message':s}))
    #return HttpResponse(s)
    return render_to_response('index.html', {'message':s})
    #return render_to_response('index.html', locals())

"""
def importHack(request):
    import csv

    lls=[]
    f = csv.reader(open('/Users/albert/stuff/CoPress/copressmoney/20100104ledger.csv'), delimiter=',', quotechar='"')
    for row in f:
        lls.append(row)

    llo=[]

    for ls in lls:
        l=LedgerLine(date=ls[1],title=ls[3],description=ls[4],documentation=ls[5],category=ls[6])
        if ls[7]!='':
            l.revenue=ls[7]
        if ls[8]!='':
            l.expenses=ls[8]
        if ls[9]!='':
            l.cash=ls[9]
        if ls[10]!='':
            l.unearned=ls[10]
        if ls[11]!='':
            l.prepaid=ls[11]
        if ls[12]!='':
            l.acctsreceivable=ls[12]
        if ls[13]!='':
            l.acctspayable=ls[13]
        llo.append(l)

    for l in llo:
        try: 
            l.save()
        except:
            print l

    return render_to_response('index.html', {'message':'imported'})
"""
