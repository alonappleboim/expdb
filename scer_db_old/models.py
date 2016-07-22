#
# The two basic objects handled by the DB are fastq files, and genomic track files (bed/wig/others). Note that the DB is
# for data generated by the lab, but also to data from other publications.
# These files are managed by introducing several objects:
#
# designs - An experimental design, e.g. MNase time course in response to salt with/without auxin-degradation, in 2 repeats.
#
# experiments - A single instantiation of an experimetnal design, performed by someone, at a specific date.
#
# samples - A single entry in an experiment, e.g. "MNase auxin induced, 15 minutes salt, in YPD, repeat 1".
#           This is essentially the metadata of a single fastq file.
#
# tracks - A genomic output from an analysis performed on a sample, together with the analysis (code+paramaters+comments)
#          performed to get from the fastq to the track file.
#
from sqlalchemy import (create_engine, MetaData, Table, Column, Integer, LargeBinary,
                        String, DateTime, Float, ForeignKey)
from sqlalchemy.orm import mapper, relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()

expfile = Table('experiment_file', Base.metadata,
                Column('exp_id', Integer, ForeignKey('experiment.id')),
                Column('file_id', Integer, ForeignKey('file.id')))

protfile = Table('protocol_file', Base.metadata,
                 Column('protocol_id', Integer, ForeignKey('protocol.id')),
                 Column('file_id', Integer, ForeignKey('file.id')))


class Experiment(Base):
    __tablename__ = 'experiment'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User")
    date = Column(DateTime, nullable=False)
    description = Column(String(2048), nullable=False)
    publication_url = Column(String(1024))
    data_url = Column(String(1024), doc='URL of GEO entry (or other repository)')
    additional_files = relationship("File", secondary=expfile)
    samples = relationship("Sample")


class File(Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    path = Column(String(2048), nullable=False)
    description = Column(String(2048), nullable=False)


class Sample(Base):
    __tablename__ = 'sample'
    id = Column(Integer, primary_key=True, nullable=False)
    experiment_id = Column(Integer, ForeignKey("experiment.id"), nullable=False)
    experiment = relationship("experiment", back_populates="samples")
    sequencing_date = Column(DateTime, nullable=False)
    fastq_path = Column(String(1024))
    comment = Column(String(2048))
    genotype_id = Column(Integer, ForeignKey("genotype.id"), nullable=False)
    genotype = relationship("Genotype")
    protocol_id = Column(Integer, ForeignKey("protocol.id"), nullable=False)
    protocol = relationship("Protocol")


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(32))


class Genotype(Base):
    __tablename__ = 'genotype'
    id = Column(Integer, primary_key=True)
    string = Column(String(1024), nullable=False)
    description = Column(String(1024))
    storage = Column(String(1024))


class Protocol(Base):
    __tablename__ = 'protocol'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    description = Column(String(2048), nullable=False)
    additional_files = relationship("File", secondary=protfile)


class Variable(Base):
    __tablename__ = 'variable'
    id = Column(Integer, primary_key=True)
    type = Column(String(8), nullable=False)
    name = Column(String(64), unique=True, nullable=False)
    units = Column(String(64), nullable=False)


class Value(Base):
    __tablename__ = 'value'
    sample_id = Column(Integer, ForeignKey('sample.id'), primary_key=True)
    sample = relationship('Sample')
    variable_id = Column(Integer, ForeignKey('variable.id'), primary_key=True)
    variable = relationship('Variable')
    value = Column(String(64), nullable=False)

    def __init__(self, variable, sample, value):
        self.variable = variable
        self.sample = sample
        self.value = value


class Track(Base):
    __tablename__ = 'track'
    id = Column(Integer, primary_key=True)
    sample_id = Column(Integer, ForeignKey("sample.id"), nullable=False)
    name = Column(String(64), nullable=False)
    comments = Column(String(2048))
    type_id = Column(Integer, ForeignKey("track_type.id"), nullable=False)
    sample_to_track = Column(LargeBinary, nullable=False,
                             doc='everything required to transition from the fastq to this track - scripts, commmandlines, etc.')
    sample_to_track_accesories = Column(LargeBinary, nullable=False)


class TrackType(Base):
    __tablename__ = 'track_type'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)