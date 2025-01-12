from django.urls import path
from . import views
#from .views import PresentCardView#, #CheckNFCStatus, NFCReadView, UpdateCustomerBalance
from .webviews.StoreLogListView import StoreLogListView

from .views import API_ReadNFCBlocking


urlpatterns = [
    path('logs/', StoreLogListView.as_view(), name='store_logs'),

    # APIs
    #path('notify/barcode/', notify_barcode_read, name='notify_barcode'),
    path('api/read/nfc-blocking/', API_ReadNFCBlocking.as_view(), name='read_nfc_blocking'),
]
