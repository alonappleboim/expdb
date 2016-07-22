from django.conf.urls import url

from . import views

urlpatterns = [url(r'upload_experiment$', views.upload_experiment)]