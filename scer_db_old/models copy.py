from __future__ import unicode_literals

from django.db import models
from django.core.files.storage import FileSystemStorage

meta_manager = FileSystemStorage(location='/Users/user/Dropbox/workspace/expdb/files/meta_files')
fastq_manager = FileSystemStorage(location='/Users/user/Dropbox/workspace/expdb/files/fastq')


class User(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(storage=meta_manager, upload_to='user_images')


class ModelWithFile(models.Model):
    pass


class Genotype(ModelWithFile):
    string = models.CharField(max_length=1000)


class Protocol(ModelWithFile):
    string = models.CharField(max_length=1000)


class File(models.Model):
    attached_to = models.ForeignKey(ModelWithFile, on_delete=models.CASCADE, related_name='files')
    upload_date = models.DateTimeField()
    file = models.FileField(storage=meta_manager)


class Experiment(ModelWithFile):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='experiments')
    performed_on = models.DateTimeField(help_text='the date on which experiment was perfomed')
    short_name = models.CharField(max_length=120, help_text='short description of the experiment (max 120 chars)')
    description = models.CharField(max_length=2000)
    publication_url = models.URLField(help_text='if published, link to publication')
    data_url = models.URLField(help_text='if data is published, link to data repository entry')


# class Sample(models.Model):
#     experiment = models.ForeignKey(experiment)#on_delete=models.PROTECT, related_name='samples')
#     sequencing_date = models.DateTimeField('date published')
#     sequencing_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sequenced_samples')
#     fastq = models.FileField(storage=fastq_manager)
#     comment = models.CharField(max_length=2000)
#     genotype = models.ForeignKey(Genotype, on_delete=models.PROTECT, related_name='samples')
#     protocol = models.ForeignKey(Protocol, on_delete=models.PROTECT, related_name='samples')
#     variables = models.ManyToManyField('Variable', through='Value')
#
#
# class Variable(models.Model):
#     name = models.CharField(max_length=100)
#     units = models.CharField(max_length=100)
#     samples = models.ManyToManyField(Sample, through='Value')


# class StringVariable(Variable):
#     def values(self):
#         return self.value_set
#
#     class Meta:
#         proxy = True
#
#
# class IntegerVariable(Variable):
#     def values(self):
#         return (int(x) for x in self.value_set)
#
#     class Meta:
#         proxy = True
#
#
# class FloatVariable(Variable):
#     def values(self):
#         return (float(x) for x in self.value_set)
#
#     class Meta:
#         proxy = True
#
#
# class Value(models.Model):
#     var = models.ForeignKey(Variable, on_delete=models.CASCADE, related_name='value_set')
#     sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
#     value = models.CharField(max_length=100)
#
#
# class TrackType(models.Model):
#     name = models.CharField(max_length=30)
#
#
# class Track(models.Model):
#     sample = models.ForeignKey(Sample, on_delete=models.PROTECT, related_name='tracks')
#     name = models.CharField(max_length=64)
#     description = models.CharField(max_length=2000)
#     type = models.ForeignKey(TrackType, on_delete=models.PROTECT, related_name='tracks')
#     generations_code = models.FileField(storage=meta_manager, upload_to='track_generation_code',
#                                         help_text=('A tar archive containing a script to generate the track from the '
#                                                    'sample fastq, with all relevant programs, versions, parameters, '
#                                                    'etc.'))
