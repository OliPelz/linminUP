# --------------------------------------------------
# File Name: setup_0.62a.py
# Purpose:
# Creation Date: 20-11-2015
# Last Modified: Fri Nov 20 13:26:55 2015
# Author(s): The DeepSEQ Team, University of Nottingham UK
# Copyright 2015 The Author(s) All Rights Reserved
# Credits: 
# --------------------------------------------------

#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe
import sys

sys.path.append('modules')

ver = '0.62a'


setup(console=['getmodels.py'
		, 'gui.py'
		, 'mincontrol.py'
		, 'minup.v' + ver + '.py'],
    options = {'py2exe': 
	{ #'compressed': True
	#, 'bundle_files': 1
	'includes': 
    		[ 'h5py.*'
		, 'pycuda.*'
		, "psutil.*"
    		, 'cython.*'
    		, 'scipy.linalg.cython_blas'
    		, 'scipy.linalg.cython_lapack'
    		, 'scipy.sparse.csgraph._validation'
    		, 'mlpy.*']
	, 'dll_excludes': 
		['MSVCP90.dll'
		, 'libgobject-2.0-0.dll'
                , 'libglib-2.0-0.dll'
		, 'libgthread-2.0-0.dll'
		, 'nvcuda.dll'
		]
        , 'excludes': 
		[ 'IPython.*'
		, 'tcl.*'
		, 'Tkinter.*'
		, 'scipy.*'
		]
	}})  


exit()

'''
"sklearn.*"
"scipy.special.*"
"scipy.special._ufuncs_cxx"
'''

