from django.views.generic import list_detail
from django.shortcuts import get_object_or_404, render_to_response
from django.http import Http404, HttpResponse

import datetime

from ledger.models import *


"""Views"""

def ledger_all(request):
    """Returns a ledger with all entries"""
    queryset = LedgerLine.objects.all()
    return list_detail.object_list(
        request,
        queryset = queryset,
        template_name = 'ledger_sheet.html',
        template_object_name = 'line',
        extra_context = {'summary': sumAccounts(queryset)},
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
        extra_context = {'summary': sumAccounts(queryset)},
    )

def ledger_year(request, year):
    """Returns a filtered set with only entries from year"""
    queryset = LedgerLine.objects.filter(date__year=year).order_by('date')
    return list_detail.object_list(
        request,
        queryset = queryset,
        template_name = 'ledger_sheet.html',
        template_object_name = 'line',
        extra_context = {'summary': sumAccounts(queryset)},
    )

def ledger_month(request, year, month):
    """Returns a filtered set with only entries from year"""
    month=int(month)
    if month<1 or month>12:
        raise Http404
    
    queryset = LedgerLine.objects.filter(date__year=year, date__month=month).order_by('date')
    return list_detail.object_list(
        request,
        queryset = queryset,
        template_name = 'ledger_sheet.html',
        template_object_name = 'line',
        extra_context = {'summary': sumAccounts(queryset)},
    )

def ledger_quarter(request, year, quarter):
    """Returns a filtered set with only entries from year"""
    quarter = int(quarter)
    year = int(year)
    if quarter == 1:
        start_date, end_date = datetime.date(year, 1, 1), datetime.date(year, 3, 31)
    elif quarter == 2:
        start_date, end_date = datetime.date(year, 4, 1), datetime.date(year, 6, 30)
    elif quarter == 3:
        start_date, end_date = datetime.date(year, 7, 1), datetime.date(year, 9, 30)
    elif quarter == 4:
        start_date, end_date = datetime.date(year, 10, 1), datetime.date(year, 12, 31)
    else:
        raise Http404
    
    queryset =  LedgerLine.objects.filter(date__range=(start_date, end_date)).order_by('date')
    return list_detail.object_list(
        request,
        queryset = queryset,
        template_name = 'ledger_sheet.html',
        template_object_name = 'line',
        extra_context = {'summary': sumAccounts(queryset)},
    )

def ledger_constraint_failed(request):
    """Returns view of all entries which fail to pass the accounting constraint and are likely erronous"""
    queryset = LedgerLine.objects.all()
    bad = []
    for line in queryset:
        if line.checkAcctConstraint() != True:
            bad.append(line)
    return list_detail.object_list(
        request,
        queryset = bad,
        template_name = 'ledger_sheet.html',
        template_object_name = 'line',
        extra_context = {'summary': sumAccounts(bad)},
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
        #validate the accounting constraints
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
    line_id = int(line_id)
    l = LedgerLine.objects.get(pk=line_id)
    if request.method == 'GET':
        form = LineForm(instance=l)
        head = 'Update Line (%d)' % line_id
        classes = 'editlineform editlineform-%d' % line_id
        submitID = "editSubmitButton-%d" % line_id
        form.auto_id = 'id_%s_'+str(form.initial['id']) #Makes input id attr's more unique, when multiple forms are present.
        return render_to_response('ledger_lineform.html', {'form': form, 'heading': head, 'submitButton': {'id': submitID, 'text': "Update Line"}, 'tr_classes': classes});
    elif request.method == 'POST':
        form = LineForm(request.POST, instance=l)
        line = form.save()
        return render_to_response('ledger_line.html', {'line': line})
    else:
        raise Http404


"""Helper Functions"""

def sumAccounts(queryset):
    """Summarizes the account changes over a time period. Takes a query set as an argument. Returns a dictionary."""
    revenue,expenses,cash,unearned,prepaid,acctsreceivable,acctspayable = 0,0,0,0,0,0,0
    for l in queryset:
        try:
            revenue+=l.revenue
        except TypeError:
            pass
        try:
            expenses+=l.expenses
        except TypeError:
            pass
        try:
            cash+=l.cash
        except TypeError:
            pass
        try:
            unearned+=l.unearned
        except TypeError:
            pass
        try:
            prepaid+=l.prepaid
        except TypeError:
            pass
        try:
            acctsreceivable+=l.acctsreceivable
        except TypeError:
            pass
        try:
            acctspayable+=l.acctspayable
        except TypeError:
            pass
    return {'revenue': revenue, 'expenses': expenses, 'cash': cash, 'unearned': unearned, 'prepaid': prepaid, 'acctsreceivable': acctsreceivable, 'acctspayable': acctspayable}
