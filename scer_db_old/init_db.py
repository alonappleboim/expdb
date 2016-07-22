from random import randint

pw = ''.join(chr(randint(40, 60)) for i in range(1, 3))
res = raw_input("DELETE the DB??? repeat the following sequence for verification: " + str(pw) + "\n")
if not res == pw:
    print "Incorrect sequence. aborting."
    exit()

import shutil, os
from config import *
from models import *
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

engine = create_engine("mysql+mysqldb://{user}:{pwd}@{server}/{db}".format(**connection_info),pool_recycle=3600)

print "Deleting DB..."
Base.metadata.drop_all(engine)
#
# print "And files..."
# shutil.rmtree(file_repository, ignore_errors=True)
#
# print "Regenerating DB..."
# Base.metadata.create_all(engine)
#
# session = sessionmaker(bind=engine)()

## basic unit test
# u = User()
# u.name = 'temp'
# session.add(u)
#
# tt = TrackType()
# tt.name = 'bigwig'
# session.add(tt)
#
# g = Genotype()
# g.string = 'hho1::ura3'
# session.add(g)
#
# p = Protocol()
# p.name = 'mnase-seq'
# p.description = 'this is a test'
# session.add(p)
#
# vt1 = VariableType()
# vt1.type = 'Integer'
# vt2 = VariableType()
# vt1.type = 'Categorical'
# session.add(vt1)
# session.add(vt2)
#
# v1 = Variable()
# v1.name = 'KCL'
# v1.units = 'M'
# v1.variable_type = vt2
# session.add(v1)
# v2 = Variable()
# v2.name = 'time'
# v2.units = 'minutes'
# v2.variable_type = vt2
# session.add(v1)
# session.add(v2)
# session.commit()
#
# from datetime import datetime
# e = Experiment()
# e.description = 'bla bla'
# e.publication_url = 'http://pub'
# e.data_url = 'http://data'
# e.user = u
# e.date = datetime.strptime('11/11/2011','%d/%m/%Y')
# session.add(e)
# session.commit()
#
# d1 = Design()
# d1.experiment = e
# d1.variable = v1
# d1.dim = 1
# d2 = Design()
# d2.experiment = e
# d2.variable = v2
# d2.dim = 3
# session.add(d1)
# session.add(d2)
# session.commit()
#
# s = Sample()
# s.sequencing_date = datetime.strptime('12/11/2011','%d/%m/%Y')
# s.comment = 'this is a comment about this sample'
# s.design_slot = 1
# s.experiment = e
# s.fastq_path = r'this\is\a\path'
# s.genotype = g
# s.protocol = p
# session.add(s)
# session.commit()
#
# val1 = Value()
# val1.sample = s
# val1.variable = v1
# val1.value = 'rr'