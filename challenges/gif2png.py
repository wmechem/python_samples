# -*- coding: utf-8 -*-
#!/usr/local/bin/python

"""
Created on Mon Apr  4 12:13:14 2016

@author: will


Write a command line utility called gif2png that takes a single command line
argument (the name of a GIF file), opens the GIF file,
converts the IMage format to PNG and stores the converted IMage as a new
PNG file in the current working directory.

Usage:

python gif2png path_to/myfile.gif

Converts GIF to PNG and saves myfile.png to current directory

Remember to "chmod +x gif2png" to run from command line without
explicitly invoking python.

pylint 5/26/2016
flake8 5/26/2016

"""

import Image
import sys
import os

GIF_FILE = sys.argv[1]
HEAD, TAIL = os.path.split(GIF_FILE)
PRE, EXT = os.path.splitext(TAIL)
PNG_FILE = PRE + '.png'
OS_CWD = os.getcwd()

print "Converting %s to 'PNG'" % str(GIF_FILE)
print "Saving output file as %s " % str(OS_CWD+"/"+PNG_FILE)

IM = Image.open(GIF_FILE)
IM.save(PNG_FILE, 'PNG')

print "Done"
