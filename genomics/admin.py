from django.contrib import admin
from django import forms
# Register your models here.

from .models import *


class MemberAdmin(admin.ModelAdmin):
    pass


class TabularSample(admin.TabularInline):
    formfield_overrides = {models.TextField: {'widget': forms.Textarea(attrs={'rows': 1, 'cols': 40})}}
    model = Sample
    extra = 5


class TabularFile(admin.TabularInline):
    formfield_overrides = {models.TextField: {'widget': forms.Textarea(attrs={'rows': 1, 'cols': 60})}}
    model = File
    extra = 1


# class ExperimentForm(forms.ModelForm):
#     samples_file = forms.FileField()
#
#     class Meta:
#         model = Experiment
#         fields = '__all__'


class ExperimentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('title',
                       'description',
                       'pub_url',
                       'data_url',
                       ('performed_by',
                        'performed_on'),
                       'variables'),
            'description': ""
        }),
    )

    list_display = ('title', 'performed_by', 'performed_on', 'n_samples')
    inlines = [TabularFile, TabularSample]
    filter_horizontal = ('variables',)
    formfield_overrides = {models.TextField: {'widget': forms.Textarea(attrs={'rows': 6, 'cols': 100})}}
    list_filter = ('performed_by', 'performed_on', 'variables')


class ModelWithFileAdmin(admin.ModelAdmin):
    inlines = [TabularFile]


class TrackAdmin(admin.ModelAdmin):
    pass


class TrackTypeAdmin(admin.ModelAdmin):
    pass


class VariableAdmin(admin.ModelAdmin):
    pass


class ValueAdmin(admin.ModelAdmin):
    fields = (('sample', 'var'), 'string_value')


admin.site.register(Value, ValueAdmin)
admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(Genotype, ModelWithFileAdmin)
admin.site.register(Protocol, ModelWithFileAdmin)
admin.site.register(Track, TrackAdmin)
admin.site.register(TrackType, TrackTypeAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Variable, VariableAdmin)
