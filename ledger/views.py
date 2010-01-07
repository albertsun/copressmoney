from django.views.generic import list_detail
from django.shortcuts import get_object_or_404
from django.http import Http404

import datetime

from ledger.models import *


"""Views"""

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


def add_line(request):
    """Handles a JavaScript request by returning the HTML of a form as a response."""
    if request.method == 'GET':
        #return HttpResponse with form
        pass
    elif request.method == 'POST':
        #submit data to database, return JSON object for one line of table
        pass


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
