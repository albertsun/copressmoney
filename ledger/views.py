from django.views.generic import list_detail
from django.shortcuts import get_object_or_404

from ledger.models import *


def ledger_client(request, client_id):
    """A view that returns a generic list_detail view of only the ledger entries associated with the client_id"""
    
    client = get_object_or_404(Client, id=client_id)
    return list_detail.object_list(
        request,
        queryset = LedgerLine.objects.filter(client=client),
        template_name = 'ledger_sheet.html',
        template_object_name = 'line',
    )
