from django import forms


class UploadExperimentForm(forms.Form):
    experiment_file = forms.FileField()
