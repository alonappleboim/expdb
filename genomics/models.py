from __future__ import unicode_literals

from django.db import models
from django.core.files.storage import FileSystemStorage
from django.utils.encoding import python_2_unicode_compatible

fss = FileSystemStorage(location='/Users/user/Dropbox/workspace/expdb/files/')


@python_2_unicode_compatible
class Member(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self): return self.name


class ModelWithFile(models.Model): pass


@python_2_unicode_compatible
class Genotype(ModelWithFile):
    short_name = models.CharField(max_length=60)
    string = models.TextField(help_text='string describing the complete genotype unambiguously')

    def __str__(self): return self.short_name


@python_2_unicode_compatible
class Protocol(ModelWithFile):
    short_name = models.CharField(max_length=60)
    description = models.TextField(max_length=2000)
    pub_url = models.URLField(help_text='if published, link to protocol', blank=True, verbose_name='publication url')

    def __str__(self): return self.short_name


@python_2_unicode_compatible
class Variable(models.Model):
    STR = 'STR'
    INT = 'INT'
    FLT = 'FLT'
    TYPES = ((STR, 'string'), (INT, 'integer'), (FLT, 'float'))
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=3, choices=TYPES, default=STR)
    units = models.CharField(max_length=100)
    samples = models.ManyToManyField('Sample', through='Value')

    def __str__(self): return '%s [%s]' % (self.name, self.units)


@python_2_unicode_compatible
class File(models.Model):
    attached_to = models.ForeignKey(ModelWithFile, on_delete=models.CASCADE, related_name='additional_files')
    upload_time = models.DateField(auto_now=True)
    file = models.FileField(storage=fss, upload_to='meta/')
    description = models.TextField(max_length=2000, blank=True)

    def __str__(self): return self.file.name


@python_2_unicode_compatible
class Experiment(ModelWithFile):
    performed_by = models.ForeignKey(Member, on_delete=models.PROTECT, related_name='experiments')
    performed_on = models.DateField(help_text='the date on which experiment was perfomed', verbose_name='on')
    title = models.CharField(max_length=120, help_text='short description of the experiment (max 120 chars)')
    description = models.TextField(max_length=2000)
    pub_url = models.URLField(help_text='if published, link to publication', blank=True, verbose_name='publication url')
    data_url = models.URLField(help_text='if data is published, link to data repository entry', blank=True)
    variables = models.ManyToManyField(Variable)

    # @property
    def n_samples(self):
        return len(self.samples.all())

    def __str__(self):
        return self.title


class Sample(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.PROTECT, related_name='samples')
    sequencing_date = models.DateField('sequencing date')
    seqeunced_by = models.ForeignKey(Member, on_delete=models.PROTECT, related_name='sequenced_samples')
    fastq = models.FileField(storage=fss, upload_to='fastq/')
    comment = models.TextField(max_length=2000, blank=True)
    genotype = models.ForeignKey(Genotype, on_delete=models.PROTECT, related_name='samples')
    protocol = models.ForeignKey(Protocol, on_delete=models.PROTECT, related_name='samples')
    variables = models.ManyToManyField(Variable, through='Value')

    def __str__(self): return '%s: %s' % (str(self.experiment), str(id(self)))


@python_2_unicode_compatible
class Value(models.Model):
    var = models.ForeignKey(Variable, on_delete=models.CASCADE, related_name='value_set')
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    string_value = models.CharField(max_length=100)

    def __str__(self): return self.string_value

    def _value(self):
        if self.var.type == Variable.INT:
            return int(self._value)
        elif self.var.type == Variable.FLT:
            return float(self._value)
        elif self.var.type == Variable.STR:
            return self._value
        else: raise TypeError('Unknown variable type')


@python_2_unicode_compatible
class TrackType(models.Model):
    name = models.CharField(max_length=30)
    format_description = models.TextField(help_text='either a text explaining the format, '
                                                    'or a link to such an explanation')

    def __str__(self): return self.name


@python_2_unicode_compatible
class Track(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.PROTECT, related_name='tracks')
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=2000)
    type = models.ForeignKey(TrackType, on_delete=models.PROTECT, related_name='tracks')
    generation_code = models.FileField(storage=fss, upload_to='track_generation_code/',
                                       help_text=('A tar archive containing a script to generate the track from the '
                                                  'sample fastq, with all relevant programs, versions, parameters, '
                                                  'etc.'))

    def __str__(self): return self.name