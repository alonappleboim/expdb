from django.conf.urls import url

from . import views

urlpatterns = [url(r'upload_samples:(?P<expid>[0-9]*)$', views.upload_samples)]