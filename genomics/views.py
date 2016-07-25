from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response
from models import *
from .forms import *
from formtools.wizard.views import WizardView


class ExperimentWizard(WizardView):

    def done(self, form_list, **kwargs):
        expid = parse_experiment(formlist)
        return HttpResponseRedirect('genomics/experiment/change/%i' % expid)


def parse_samples(file, exp):
    print exp.variables


def upload_samples(request, expid):
    exp = Experiment.objects.get(pk=expid)
    if request.method == 'POST':
        form = UploadSamplesForm(request.POST, request.FILES)
        if form.is_valid():
            expform = parse_samples(form.files['samples_file'], exp)
            return render(request, 'change_form_.html')
        else:
            print form.errors
    else:
        form = UploadSamplesForm()
    return render(request, 'genomics/upload_samples', {'form': form, 'exp' : exp})


def resp(request):
    return HttpResponse('this is a response')