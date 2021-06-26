#!/usr/bin/env python3

# MIT License

# Copyright (c) 2018 The University of Michigan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
import shutil
from shutil import unpack_archive
import subprocess
from subprocess import call
import gdown

tablext_src_dir = os.path.dirname(__file__)

url = 'https://umich.box.com/shared/static/fbgyle2s4zoy9fwctcwtjyp74hqclx91'
output = os.path.join(tablext_src_dir,'Table_extract_robust.zip')
gdown.download(url, output, quiet=False)

os.makedirs('Table_extract_robust')
unpack_archive('Table_extract_robust.zip', os.path.join(tablext_src_dir,'Table_extract_robust'), 'zip')

try:
	ret = subprocess.check_call(['git', 'clone', 'git@github.com:qqwweee/keras-yolo3.git'])
	if ret:
		print("Error: Command returned error: " + subprocess.CalledProcessError)
		sys.exit(1)
except:
	print ("Error/Exception occurred while running command:", sys.exc_info()[0])

try:
	shutil.move('keras-yolo3', os.path.join(tablext_src_dir,'yolo_helpers','keras_yolo3'))
except FileNotFoundError as e:
	print("Error occurred while moving Table_extract_robust.zip:")
	print("Exception: ", str(e))
	sys.exit(1)

os.remove(os.path.join(tablext_src_dir,'yolo_helpers','keras_yolo3','yolo.py'))
url_list = ['https://drive.google.com/u/0/uc?id=1jo1KO_DW2ifGaaX_o4jOrbGV-g6bouQL&export=download', 'https://drive.google.com/u/0/uc?id=1DVVlHgmebYInJE7Gyj58fqWq-NVL8RsH&export=download', 'https://drive.google.com/u/0/uc?id=1QTo0anpbvmxd0sNBdNyv-Ld30iDvyxmY&export=download', 'https://drive.google.com/u/0/uc?id=11Gx_LFV3YlbU2ui7uLOiNqFJkujommzD&export=download']
output_list = ['yolo.h5', 'yolov3.weights','yolo.py','trained_weights_1915_final.h5']
output_dir = os.path.join(tablext_src_dir,'yolo_helpers','keras_yolo3')

for i in range(len(output_list)):
	gdown.download(url_list[i], os.path.join(output_dir,output_list[i]), quiet=False)