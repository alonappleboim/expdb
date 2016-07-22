file_repository = '/cs/bd/seqdb_files/'
import os
if not os.access(os.path.abspath(file_repository), os.X_OK):
    print 'Can not continue, file repository is not write-accessible'
    exit()
efpath = file_repository + os.path.sep + 'experiment_files'
if not os.access(os.path.abspath(efpath), os.X_OK):
    os.mkdir(efpath)
pfpath = file_repository + os.path.sep + 'protocol_files'
if not os.access(os.path.abspath(pfpath), os.X_OK):
    os.mkdir(pfpath)
sfpath = file_repository + os.path.sep + 'sample_files'
if not os.access(os.path.abspath(pfpath), os.X_OK):
    os.mkdir(sfpath)
connection_info = dict(user="nirf_lab",pwd="",server="localhost",db="nirf_lab")
# connection_info = dict(user="nirf_lab",pwd="nirflab",server="dbserver",db="nirf_lab")