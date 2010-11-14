from django.conf.urls.defaults import *
from django.views.generic import list_detail
from django.conf import settings

from copressmoney.views import *
from copressmoney.ledger.models import *
from copressmoney.ledger.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from django.contrib.auth.views import login, logout

client_list = {
    'queryset': Client.objects.all(),
    'template_name': 'client_list.html',
    'template_object_name': 'client',
    'extra_context': {'title': 'Clients'}
}

urlpatterns = patterns('',
    (r'^$', home),
    (r'^clients/$', list_detail.object_list, client_list),
    (r'^ledger/all/$', ledger_all),
    (r'^ledger/current/$', ledger_current),
    (r'^ledger/client/(\d+)/$', ledger_client),

    (r'^ledger/year/(\d\d\d\d)/$', ledger_year),
    (r'^ledger/year/(\d\d\d\d)/quarter/(\d)/$', ledger_quarter),
    (r'^ledger/year/(\d\d\d\d)/month/(\d\d?)/$', ledger_month),

    (r'^ledger/constraint_failed/$', ledger_constraint_failed),

    (r'^api/add/line/$', add_line),
    (r'^api/edit/line/(\d+)/$', edit_line),
    (r'^api/delete/line/(\d+)/$', delete_line),
    (r'^api/get/line/(\d+)/$', get_line),

    (r'^api/add/sale/$', add_sale),

    (r'^display_meta/$', display_meta),
    #(r'^help/$', view_help),

    #(r'^ledger/import/$', importHack),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^login/$', login, {'template_name': 'login.html'}),
    (r'^logout/$', logout),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/albert/Desktop/copressmoney/templates/static'}),
        (r'^debug/$', view_debug),
    )
    
