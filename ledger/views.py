from django.views.generic import list_detail
from django.shortcuts import get_object_or_404, render_to_response
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.db.models import Sum
#from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.utils import simplejson

import datetime

from copressmoney.ledger.models import *
from copressmoney.ledger.forms import *

"""Views"""

def ledger_all(request):
    """Returns a ledger with all entries"""
    queryset = LedgerLine.objects.all()
    #queryset.aggregate(Sum('revenue')) example aggregation....
    return list_detail.object_list(
        request,
        queryset = queryset,
        template_name = 'ledger_sheet.html',
        template_object_name = 'line',
        extra_context = {'title': 'All Ledger Entries'},
    )

def ledger_current(request):
    """Returns a ledger with all entries"""
    queryset = LedgerLine.objects.filter(date__lte=datetime.datetime.now()).order_by('-date')
    #queryset.aggregate(Sum('revenue')) example aggregation....
    return list_detail.object_list(
        request,
        queryset = queryset,
        template_name = 'ledger_sheet.html',
        template_object_name = 'line',
        extra_context = {'title': 'Current Ledger Entries'},
    )

def ledger_client(request, client_id):
    """A view that returns a generic list_detail view of only the ledger entries associated with the client_id"""
    client = get_object_or_404(Client, id=client_id)
    queryset = LedgerLine.objects.filter(client=client)
    return list_detail.object_list(
        request,
        queryset = queryset,
        template_name = 'ledger_sheet.html',
        template_object_name = 'line',
        extra_context = {'title': '('+client.name+') Client Ledger Entries'},
    )

def ledger_year(request, year):
    """Returns a filtered set with only entries from year"""
    year = int(year)
    queryset = LedgerLine.objects.filter(date__year=year).order_by('-date')
    return list_detail.object_list(
        request,
        queryset = queryset,
        template_name = 'ledger_sheet.html',
        template_object_name = 'line',
        extra_context = {'title': '('+str(year)+') Ledger Entries', 'priorbalance': sumAccounts(LedgerLine.objects.filter(date__lt=datetime.date(year, 1, 1))), 'nav': {'prev': '/ledger/year/'+str(year-1)+'/', 'next': '/ledger/year/'+str(year+1)+'/'} },
    )

def ledger_month(request, year, month):
    """Returns a filtered set with only entries from year"""
    year = int(year)
    month = int(month)
    if month<1 or month>12:
        raise Http404
    
    prev = "/ledger/year/"
    prev += '%s/month/' % (str(year-1) if (month==1) else str(year))
    prev += '%s/' % ('12' if (month==1) else str(month-1))
    next = "/ledger/year/"
    next += '%s/month/' % (str(year+1) if (month==12) else str(year))
    next += '%s/' % ('1' if (month==12) else str(month+1))

    queryset = LedgerLine.objects.filter(date__year=year, date__month=month).order_by('-date')
    return list_detail.object_list(
        request,
        queryset = queryset,
        template_name = 'ledger_sheet.html',
        template_object_name = 'line',
        extra_context = {'title': '(M'+str(month)+' '+str(year)+') Ledger Entries', 'priorbalance': sumAccounts(LedgerLine.objects.filter(date__lt=datetime.date(year, month, 1))), 'nav': {'prev': prev, 'next': next} },
    )

def ledger_quarter(request, year, quarter):
    """Returns a filtered set with only entries from year"""
    quarter = int(quarter)
    year = int(year)
    if quarter == 1:
        start_date, end_date = datetime.date(year, 1, 1), datetime.date(year, 3, 31)
        month = 1
    elif quarter == 2:
        start_date, end_date = datetime.date(year, 4, 1), datetime.date(year, 6, 30)
        month = 4
    elif quarter == 3:
        start_date, end_date = datetime.date(year, 7, 1), datetime.date(year, 9, 30)
        month = 7
    elif quarter == 4:
        start_date, end_date = datetime.date(year, 10, 1), datetime.date(year, 12, 31)
        month = 10
    else:
        raise Http404

    prev = "/ledger/year/"
    prev += '%s/quarter/' % (str(year-1) if (quarter==1) else str(year))
    prev += '%s/' % ('4' if (quarter==1) else str(quarter-1))
    next = "/ledger/year/"
    next += '%s/quarter/' % (str(year+1) if (quarter==4) else str(year))
    next += '%s/' % ('1' if (quarter==4) else str(quarter+1))
    
    queryset =  LedgerLine.objects.filter(date__range=(start_date, end_date)).order_by('-date')
    return list_detail.object_list(
        request,
        queryset = queryset,
        template_name = 'ledger_sheet.html',
        template_object_name = 'line',
        extra_context = {'title': '(Q'+str(quarter)+' '+str(year)+') Ledger Entries', 'priorbalance': sumAccounts(LedgerLine.objects.filter(date__lt=datetime.date(year, month, 1))), 'nav': {'prev': prev, 'next': next} },
    )

def ledger_constraint_failed(request):
    """Returns view of all entries which fail to pass the accounting constraint and are likely erronous"""
    queryset = LedgerLine.objects.all()
    bad = []
    for line in queryset:
        if line.checkAcctConstraint() != True:
            bad.append(line)
    
    #hack so its possible to pass a list to the list_detail.object_list generic view instead of a QuerySet
    class ListQS(list):
        def _clone(self):
            return self[:]
    bad = ListQS(bad)

    return list_detail.object_list(
        request,
        queryset = bad,
        template_name = 'ledger_sheet.html',
        template_object_name = 'line',
        extra_context = {'title': 'Entries Failing Accounting Constraint'},
    )


"""
These need to return validation errors better, and in a javascript compatible format so that they can be shown to the user.
"""

def add_line(request):
    """Handles a JavaScript request by returning the HTML of a form as a response.
    URL at /api/add/line/
    GET: returns HTML of a line submission form.
    POST: submits a line to a database and returns the line formatted in a table, within <tr> tags.
    """
    if request.method == 'GET':
        form = LineForm()
        form.auto_id = 'id_%s_add' #Makes input id attr's more unique, when multiple forms are present.
        """
        The non-shortcut way:
        t = get_template('js_addline.html')
        html = t.render(Context({'form': form}))
        return HttpResponse(html)
        """
        return render_to_response('ledger_lineform.html', {'form': form, 'heading': "Add New Line", 'submitButton': {'id': "addlineSubmitButton", 'text': "Add Line"}, 'tr_classes': "addlineform"})
    elif request.method == 'POST':
        form = LineForm(request.POST)
        line = form.save()
        return render_to_response('ledger_line.html', {'line': line})
    else:
        raise Http404

def edit_line(request, line_id):
    """Handles a JavaScript by returning the HTML of a form prefilled with a line to edit.
    URL at /api/edit/line/(line_id)/
    GET: returns HTML of a line to edit
    POST: updates line in database, returns edited line in <tr> tags
    """
    try:
        line_id = int(line_id)
        l = LedgerLine.objects.get(pk=line_id)
    except (TypeError, LedgerLine.DoesNotExist):
        return HttpResponseBadRequest('{ "status": "failed", "message": "Must provide valid line id" }')
    if request.method == 'GET':
        form = LineForm(instance=l)
        head = 'Update Line (%d)' % line_id
        classes = 'editlineform editlineform-%d' % line_id
        submitID = "editSubmitButton-%d" % line_id
        form.auto_id = 'id_%s_'+str(form.initial['id']) #Makes input id attr's more unique, when multiple forms are present.
        
        #need to pass additional context to the template, a string with id's i.e. '477,475,474' because that part of the form is custom implemented in javascript
        relatedvalues = ",".join([str(r.id) for r in l.related.all()])

        return render_to_response('ledger_lineform.html', {'form': form, 'relatedvalues': relatedvalues, 'heading': head, 'submitButton': {'id': submitID, 'text': "Update Line"}, 'tr_classes': classes});
    elif request.method == 'POST':
        form = LineForm(request.POST, instance=l)

        line = form.save()
        return render_to_response('ledger_line.html', {'line': line})
    else:
        raise Http404

def delete_line(request, line_id):
    """Handles a GET request to delete a line.
    URL at /api/delete/line/(line_id)/
    GET: delete's line_id, returns success message
    """
    try:
        line_id = int(line_id)
        l = LedgerLine.objects.get(pk=line_id)
        assert(request.method == 'GET')
        l.delete()
        return HttpResponse('{ "status": "success", "deleted": %d }' % line_id)
    except (TypeError, LedgerLine.DoesNotExist, AssertionError):
        return HttpResponseBadRequest('{ "status": "failed" }')

def get_line(request, line_id):
    """Returns a single lne of the ledger.
    URL at /api/get/line/(line_id)/"""
    try:
        line_id = int(line_id)
        l = LedgerLine.objects.get(pk=line_id)
        return render_to_response('ledger_line.html', {'line': l})
    except LedgerLine.DoesNotExist:
        raise Http404

def add_sale(request):
    """Returns a form for entering a new sale into the ledger.
    URL at /api/add/sale/
    GET: return's a custom form
    POST: processes the sale and creates all the ledger lines associated with it and relates them
    """
    if request.method == 'GET':
        form = SaleForm()
        form.auto_id = 'id_%s_addsale' #May not be necessary.
        return render_to_response('saleform.html', {'form': form, 'heading': "Record New Sale", 'submitButton': {'id': "addsaleSubmitButton", 'text': "Record Sale"}, 'div_classes': "addsaleform"}, context_instance=RequestContext(request))
    elif request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            lines = form.save()
            #form should return a JSON representation of the new lines that have to be added, OR of errors
            return HttpResponse(simplejson.dumps(lines))
        else:
            raise Http404
    else:
        raise Http404

"""Helper Functions"""

def sumAccounts(queryset):
    """Summarizes the account changes over a time period. Takes a query set as an argument. Returns a dictionary."""
    revenue,expenses,cash,unearned,prepaid,acctsreceivable,acctspayable = 0,0,0,0,0,0,0
    
    aggregates = queryset.aggregate(Sum('revenue'), Sum('expenses'), Sum('cash'), Sum('unearned'), Sum('prepaid'), Sum('acctsreceivable'), Sum('acctspayable'))
    revenue = aggregates['revenue__sum']
    expenses = aggregates['expenses__sum']
    cash = aggregates['cash__sum']
    unearned = aggregates['unearned__sum']
    prepaid = aggregates['prepaid__sum']
    acctsreceivable = aggregates['acctsreceivable__sum']
    acctspayable = aggregates['acctspayable__sum']

    return {'revenue': revenue, 'expenses': expenses, 'cash': cash, 'unearned': unearned, 'prepaid': prepaid, 'acctsreceivable': acctsreceivable, 'acctspayable': acctspayable}
