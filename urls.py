from django.conf.urls.defaults import *
from django.views.generic import list_detail

from copressmoney.views import *
from copressmoney.ledger.models import *
from copressmoney.ledger.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

client_list = {
    'queryset': Client.objects.all(),
    'template_name': 'client_list.html',
    'template_object_name': 'client',
}
ledger_all = {
    'queryset': LedgerLine.objects.all(),
    'template_name': 'ledger_sheet.html',
    'template_object_name': 'line',
    'extra_context': {'summary': sumAccounts(LedgerLine.objects.all())},
}

urlpatterns = patterns('',
    (r'^$', home),
    (r'^clients/$', list_detail.object_list, client_list),
    (r'^ledger/all/$', list_detail.object_list, ledger_all),
    (r'^ledger/client/(\d+)/$', ledger_client),

    (r'^ledger/year/(\d\d\d\d)/$', ledger_year),
    (r'^ledger/year/(\d\d\d\d)/quarter/(\d)/$', ledger_quarter),
    (r'^ledger/year/(\d\d\d\d)/month/(\d\d?)/$', ledger_month),

    #(r'^ledger/import/$', importHack),

    # Example:
    # (r'^copressmoney/', include('copressmoney.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)


    
