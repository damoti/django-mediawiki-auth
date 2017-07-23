from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', Status.as_view(), name='status'),
]
