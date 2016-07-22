from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .forms import UploadExperimentForm


def upload_experiment(request):
    if request.method == 'POST':
        form = UploadExperimentForm(request.POST, request.FILES)
        if form.is_valid():
            return HttpResponseRedirect('/success/url/')
        else:
            print form.errors
    else:
        form = UploadExperimentForm()
        print 'not post'
    return render(request, 'genomics/upload_experiment.html', {'form': form})


def resp(request):
    return HttpResponse('this is a response')