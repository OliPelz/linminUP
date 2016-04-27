#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------------------
# File Name: run_pbs.py
# Purpose: wrapper for running shell commands in pbs queue (works with openpbs/torque)
# Creation Date: 2016
# Author(s): Oliver Pelz
# tested on Linux only
# --------------------------------------------------

import os, stat
import tempfile
import subprocess
import drmaa

# ---------------------------------------------------------------------------

# this class is for running shell commands in a clustered environment 
# using the open source openpbs / torque system
# Please note: this class needs access to a shared nfs mount (accessible on all your pbs nodes)
# because we need to create some temp files which need to be accessible from everywhere
# check if you have write access to nfs_share_dir too!
# deleteFiles parameter deletes all generated files when the program exits
class PBSUtilsDRMAA(object):
   def __init__(self, nfs_share_dir, verbose = False):
      if(not os.path.ismount(self.find_mountpoint(nfs_share_dir))):
         # TODO: throw exception, this method only works if nfs share mount is provided
         # accessible for all nodes
         print nfs_share_dir + " is not a nfs mount"
         return False
      
      self._nfs_share_dir = nfs_share_dir
      self.devnull = open(os.devnull, 'w')
      self._verbose = verbose
# this comes from stackoverflow: http://stackoverflow.com/questions/4453602/how-to-find-the-mountpoint-a-file-resides-on
# get the mountpoint for a file e.g. : /data/x/y/z/bla.txt -> /data
   def find_mountpoint(self, path):
    for l in open("/proc/mounts", "r"):
        mp = l.split(" ")[1]
        if(mp != "/" and path.find(mp)==0): return mp
    return None
   
   # cmd - the command you want to execute in pbs
   # returns the commands stdout and stderr as files
   def run_command_qsub_files(self, pbs_run_name, cmd):
      # generate temp files which hold the cmd's output
      cmdStdoutFile = tempfile.NamedTemporaryFile(dir=self._nfs_share_dir, delete=False)
      cmdStderrFile = tempfile.NamedTemporaryFile(dir=self._nfs_share_dir, delete=False)

      with drmaa.Session() as s:
         print('Creating job template')
         jt = s.createJobTemplate()
         jt.remoteCommand = os.path.join(cmd + " 1> " + cmdStdoutFile +" 2>" + cmdStderrFile )
    
         jt.joinFiles = True

         jobid = s.runJob(jt)
         print('Your job has been submitted with ID %s' % jobid)

         retval = s.wait(jobid, drmaa.Session.TIMEOUT_WAIT_FOREVER)
         print('Job: {0} finished with status {1}'.format(retval.jobId, retval.hasExited))

         print('Cleaning up')
         s.deleteJobTemplate(jt)

      return cmdStdoutFile.name, cmdStderrFile.name
 
   def run_command_qsub_output(self, pbs_run_name, cmd, delete_file = True):
     stdoutFilename, stderrFilename = self.run_command_qsub_files(pbs_run_name, cmd)
     try:
       with open(stdoutFilename) as f: stdoutFileContent = f.read()
       with open(stderrFilename) as f: stderrFileContent = f.read()
     except IOError as e:
       print "I/O error({0}): {1}".format(e.errno, e.strerror)
       return False
     return stdoutFileContent, stderrFileContent
     



