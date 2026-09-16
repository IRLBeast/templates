from django.contrib import admin
from django.urls import path
from tests_manager.views import (run_test, index, aiskr, asubs, asbdb, rinok, isip, smp,
                                 documents, biss_table, get_messages, get_message, get_outgoing_messages, get_outgoing_message, biss_mx, api_run_tests,
                                 get_messages_admin, get_message_admin)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name = 'home'),
    path('aiskr', aiskr, name = 'aiskr'),
    path('asubs', asubs, name = 'asubs'),
    path('asbdb', asbdb, name = 'asbdb'),
    path('rinok', rinok, name = 'rinok'),
    path('isip', isip, name = 'isip'),
    path('smp', smp, name = 'smp'),
    path('documents', documents, name = 'documents'),
    path('biss_table', biss_table, name = 'biss_table'),
    path("api/messages/", get_messages, name = 'get_messages'),
    path("api/message/<int:message_id>", get_message, name="get_message"),
    path("api/outgoing/<int:message_id>", get_outgoing_messages, name="get_outgoing_messages"),
    path("api/outgoing_message/<int:message_id>", get_outgoing_message, name="get_outgoing_message"),
    path("api/messages_admin", get_messages_admin, name = "get_messages_admin"),
    path("api/message_admin/<int:message_id>", get_message_admin, name="get_message_admin"),
    path('biss_mx', biss_mx, name="biss_mx"),
    path('run-tests/', run_test),
    path("api/run/", api_run_tests),
    path('smp_table', smp_table, name='smp_table'),
    path("api/smp/messages/", get_smp_messages, name="get_smp_messages"),
    path("api/smp/message/<int:message_id>", get_smp_message, name="get_smp_message"),
    path("api/smp/outgoing/<int:message_id>", get_smp_outgoing_messages, name="get_smp_outgoing_messages"),
    path("api/smp/outgoing_message/<int:message_id>", get_smp_outgoing_message, name="get_smp_outgoing_message"),
    path("api/smp/messages_admin", get_smp_messages_admin, name="get_smp_messages_admin"),
    path("api/smp/message_admin/<int:message_id>", get_smp_message_admin, name="get_smp_message_admin"),
]
