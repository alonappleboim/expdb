# -*- coding: utf-8 -*-
"""
Add, update, delete, get experiment info
@author: Alon
"""
import os, sys, csv, argparse, re

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

from scer_db_old.config import connection_info
from scer_db_old.models import *
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

engine = create_engine("mysql+mysqldb://{user}:{pwd}@{server}/{db}".format(**connection_info),pool_recycle=3600)
session = sessionmaker(bind=engine)()

from datetime import datetime

UNIT_SEP = '|'
COMMENT = '#'
MAX_EMPTY_LINES = 10
POS = {'protocol':0, 'genotype':1, 'fastq path':-1, 'sequencing date':-2}
POS_ABS = None
# sys.path.append(os.path.abspath('/cs/wetlab/Alon/Dropbox/workspace/'))


def load_user_file():
    while True:
        resp = raw_input('Please enter file path: \n')
        path = os.path.abspath(os.path.curdir+os.path.sep+resp)
        if not os.access(path, os.R_OK) or os.path.isdir(path):
            print('Could not access "%s", make sure file path is correct and you have read permissions.' % path)
            resp = ''
        else:
            desc = raw_input('Please enter a description for the file: \n')
            f = File()
            f.description = desc
            f.path = path
            return f


def err(msg):
    logger.error(msg)
    exit()


def get_user(name):
    users = session.query(User)
    for u in users:
        if name.lower() == u.name.lower(): return u
    resp = raw_input('Could not find user %s in DB, create it (yes/no)? ' % name)
    if resp == 'yes':
        u = User()
        u.name = name[0].upper()+name[1:].lower()
        session.add(u)
        session.commit()
        logging.info('Created user %s' % u.name)
        return u
    else:
        logger.error('User %s not valid' % u.name)
        exit()


def parse_header(iter, delim):
    files, exp = [], Experiment()
    try:
        i, (field, val) = iter.next()
        if field != 'user': raise ValueError
        exp.user = get_user(val)
    except ValueError: err('Expected "user%s<user>" at line %i' % (delim,i))
    try:
        i, (field, val) = iter.next()
        if field != 'date': raise ValueError
        exp.date = datetime.strptime(val.strip(), '%d/%m/%Y')
    except ValueError:
        err('Expected "date%s<DD/MM/YYYY>" at line %i' % (delim,i))
    try:
        i, (field, val) = iter.next()
        if field != 'description' or val=='': raise ValueError
        exp.description = val
    except ValueError:
        err('Expected "description%s<description>" at line %i' % (delim,i))
    try:
        i, fval = iter.next()
        if len(fval) == 2:
            if fval[0] != 'publication url': raise ValueError
            exp.publication_url = fval[1]
        else: exp.publication_url = ''
    except ValueError:
        err('Expected "publication url%s<url>" at line %i' % (delim,i))
    try:
        i, fval = iter.next()
        if len(fval) == 2:
            if fval[0] != 'data url': raise ValueError
            exp.data_url = fval[1]
        else:
            exp.data_url = ''
    except ValueError:
        err('Expected "data url%s<url>" at line %i' % (delim,i))
    resp = raw_input("Are there files associated with this experiment you'd like to upload (yes/no)? ")
    if resp == 'yes':
        while resp == 'yes':
            f = load_user_file()
            exp.additional_files.append(f)
            files.append(f)
            resp = raw_input("Load additional files (yes/no)? ")
    return files, exp


def parse_unitype(var_string):
    v_units = [x.strip() for x in var_string.split('[')[1].split(']')[0].split(UNIT_SEP)]
    # parse units/type
    if len(v_units) == 1:
        if v_units[0].lower() == 'str':
            v_type, v_units = 'str', ''
        elif v_units[0].lower() == 'num':
            v_type, v_units = 'num', ''
        else:
            v_type, v_units = 'str', ''
    else:
        if v_units[0].lower() == 'str':
            v_type, v_units = 'str', v_units[1]
        elif v_units[0].lower() == 'num':
            v_type, v_units = 'num', v_units[1]
        elif v_units[1].lower() == 'str':
            v_type, v_units = 'str', v_units[0]
        elif v_units[1].lower() == 'num':
            v_type, v_units = 'num', v_units[0]
    return v_type, v_units


def add_new_var(vname, vtype, vunits, vinfo):
    logger.info('Adding a new variable "%s" of type "%s" with units "%s".', *vinfo)
    v = Variable()
    v.name, v.type, v.units = vname, vtype.lower(), vunits
    session.add(v)
    return v


def parse_sample_header(iter):
    try:
        i, (hdr,) = iter.next()
        if hdr != 'samples:': raise ValueError
    except ValueError:
        err('Expected "samples:" between header and samples')
    try:
        i, hdr = iter.next()
        for f,p in POS.iteritems():
            msg = 'Mandatory "%s" field should be the %i column of the samples header' % (f.replace('_',' '), p)
            if hdr[p].strip() != f: err(msg)
    except ValueError:
        err('Expected sample header after "samples" line')

    global POS_ABS # fill in absolute positions
    POS_ABS = [v if v >= 0 else len(hdr)+v for v in POS.values()]

    hdr_vars = []
    for i, var_string in enumerate(hdr):
        vars = session.query(Variable).all()
        if i in POS_ABS:
            hdr_vars.append(None)
            continue
        vname = var_string.split('[')[0].strip()
        vtype, vunits = parse_unitype(var_string)
        exists = None
        for v in vars:
            if v.name.lower() == vname.lower():
                exists = v
                break
        vinfo = (vname, vtype, vunits)
        if exists is None:
            resp = raw_input('Add new variable "%s" of type "%s" with units "%s" (yes/no)? ' % vinfo)
            if resp == 'yes':
                v = add_new_var(vname, vtype, vunits, vinfo)
            else:
                err('User did not want to add a variable (%s [%s,%s]), aborting' % vinfo)
        else:
            if v.type.lower() == vtype.lower() and v.units.lower() == vunits.lower(): pass
            else:
                resp = raw_input('Existing variable has type/units %s/%s and new variable has type/units %s/%s, '
                                 'create new variable? (yes/no)? ' % (v.type, v.units, vtype, vunits))
                if resp == 'yes':
                    v = add_new_var(vname, vtype, vunits, vinfo)
                else:
                    err('User did not want to add a variable (%s [%s,%s]), aborting' % vinfo)
        hdr_vars.append(v)
    session.add_all(vars)
    session.commit() #to prevent re-prompting if there's an issue
    return hdr_vars


def parse_samples(iter, vars, exp, files):
    samples = []
    for i, sample_line in iter:
        genotypes = session.query(Genotype).all()
        protocols = session.query(Protocol).all()
        sg = sample_line[POS['genotype']]
        sp = sample_line[POS['protocol']]
        spath = sample_line[POS['fastq path']]
        sdate = sample_line[POS['sequencing date']]
        spath = os.path.abspath(spath)
        s = Sample()
        s.experiment = exp
        s.sequencing_date = datetime.strptime(sdate.strip(), '%d/%m/%Y')
        # assert file path is OK
        while not os.access(spath, os.R_OK):
            raw_input('Could not access "%s", make sure path is correct and you have read '
                      'permissions and press any key...' % spath)
        s.fastq_path = spath
        # add genotype
        found = False
        for g in genotypes:
            if g.string.lower() == sg.lower():
                found = True
                break
        if not found:
            resp = raw_input('Could not find genotype "%s" in DB, create it (yes/no)? ' % sg)
            if resp == 'yes':
                g = Genotype()
                g.string, resp = sg, ''
                while not resp:
                    resp = raw_input('Please enter a genotype description string:\n')
                g.description = resp
                resp = ''
                while not resp:
                    resp = raw_input('Please enter the genotype storage coordinate:\n')
                g.storage = resp
                session.add(g)
            else:
                err('Could not proceed with genotype %s at line %i' % (sg, i))
        s.genotype = g
        # add protocol
        found = False
        for p in protocols:
            if p.name.lower() == sp.lower():
                found = True
                break
        if not found:
            resp = raw_input('Could not find protocol "%s" in DB, create it (yes/no)? ' % sp)
            if resp == 'yes':
                p = Protocol()
                p.name, resp = sp, ''
                while not resp:
                    resp = raw_input('Please enter description for the new protocol:\n')
                p.description = resp
                resp = raw_input("Are there files associated with this protocol you'd like to upload (yes/no)? ")
                if resp == 'yes':
                    while resp == 'yes':
                        f = load_user_file()
                        p.additional_files.append(f)
                        files.append(f)
                        resp = raw_input("Load additional files (yes/no)? ")
                session.add(p)
            else:
                err('Could not proceed with protocol %s at line %i' % (sp, i))
        s.protocol = p
        samples.append(s)
        session.commit()

        #load variable values
        for j, val_string, v in zip(range(len(vars)), sample_line, vars):
            if j in POS_ABS: continue
            if v.type == 'num':
                try: int(val_string)
                except ValueError: float(val_string)
            session.add(Value(v, s, val_string))
    return samples


def next_line(f, delim): # a generator ignoring comments and empty lines
    i, ei = 0, 0
    with open(f, 'rU') as FILE:
        while True:
            i += 1
            line = FILE.readline().split(COMMENT)[0].strip(delim+'\n ')
            if line == 'end': break
            if line:
                ei = 0
                yield i, line.split(delim)
            else: ei = ei + 1
            if ei > MAX_EMPTY_LINES:
                logger.error("File shouldn't contain more than %i consecutive empty lines" % MAX_EMPTY_LINES)
                exit()

def store_files(files):
    pass

def add_experiment(args):
    path = os.path.abspath(args.instructions_path)
    [dir, fname] = os.path.split(args.instructions_path)
    iter = next_line(args.instructions_path, args.delimiter)
    files, exp = parse_header(iter, args.delimiter)
    sample_header = parse_sample_header(iter)
    samples = parse_samples(iter, sample_header, exp, files)
    store_files(files)
    session.commit()
    logger.info('Successfuly added experiment (id: %i) with %i samples.' % (exp.id,len(samples)))


def remove_experiment(args): pass


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['info','add','delete','update'], help='action to perform')
    p.add_argument('--delimiter', '-d', default=',')
    p.add_argument('instructions_path', action='store')
    args = p.parse_args()
    globals()[args.action+'_experiment'](args)
