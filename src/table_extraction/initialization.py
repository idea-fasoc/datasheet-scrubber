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

def library_installer(py_lib):
	if py_lib == 'opencv':
		import_name = 'cv2'
	else:
		import_name = py_lib
	try:
		__import__(import_name)
		print(f"Library '{py_lib}' is installed already.")
	except ImportError:
		print(f"Library '{py_lib}' is not installed. Installing with conda ...")
		try:
			subprocess.check_call(["conda", "install", "-c", "conda-forge", py_lib])
			__import__(import_name)  # Try importing again after installation
			print(f"Library '{py_lib}' installed successfully.")
		except Exception as e:
			print(f"Error installing '{py_lib}': {e}")
			print("Make sure you have Anaconda installed and added to your PATH.")
			print("You can manually install gdown using 'conda install -c conda-forge pytesseract'.")
			sys.exit(1)

library_installer("gdown")
try:
    import gdown
except ImportError:
	print("gdown is not installed. Installing with conda ...")
	try:
		subprocess.check_call(["conda", "install", "-c", "conda-forge", "gdown"])
		import gdown  # Try importing again after installation
		print("gdown has been successfully installed.")
	except Exception as e:
		print(f"Error installing gdown: {e}")
		print("Make sure you have Anaconda installed and added to your PATH.")
		print("You can manually install gdown using 'conda install -c conda-forge gdown'.")

tablext_src_dir = os.path.dirname(__file__)
url = 'https://drive.google.com/u/0/uc?id=1RFDf8LUAGTWk_SjmPLuxzxgAZDIWvCiD&export=download'
table_extract_robust_zip = os.path.join(tablext_src_dir, 'Table_extract_robust.zip')
if not os.path.exists(table_extract_robust_zip):
	try:
		gdown.download(url, table_extract_robust_zip, quiet = False)
		print("File 'Table_extract_robust.zip' downloaded successfully.")
	except Exception as e:
		print(f"Error downloading file 'Table_extract_robust.zip': {e}")
else:
 	print("File 'Table_extract_robust.zip' already exists.")

if not os.path.exists('Table_extract_robust'):
	try:
		os.makedirs('Table_extract_robust')
		print("Directory 'Table_extract_robust' created successfully.")
	except Exception as e:
		print(f"Error creating directory 'Table_extract_robust': {e}")
else:
 	print("Directory 'Table_extract_robust' already exists.")
unpack_archive('Table_extract_robust.zip', os.path.join(tablext_src_dir,'Table_extract_robust'), 'zip')

try:
	ret = subprocess.check_call(['git', 'clone', 'https://github.com/qqwweee/keras-yolo3.git'])
	if ret:
		print("Error: Command returned error: " + subprocess.CalledProcessError)
		sys.exit(1)
except:
 	print("Error/Exception occurred while running command:", sys.exc_info()[0])

try:
 	shutil.move('keras-yolo3', os.path.join(tablext_src_dir,'yolo_helpers','keras_yolo3'))
except FileNotFoundError as e:
 	print("Error occurred while moving Table_extract_robust.zip:")
 	print("Exception: ", str(e))
 	sys.exit(1)

os.remove(os.path.join(tablext_src_dir,'yolo_helpers','keras_yolo3','yolo.py'))
os.remove(os.path.join(tablext_src_dir,'yolo_helpers','keras_yolo3','yolo3','model.py'))
url_list = ['https://drive.google.com/u/0/uc?id=15imxnopP_4ILtg0V2Ni11IGtPxA-dthb&export=download', 'https://drive.google.com/u/0/uc?id=12-sLCv6m4z---qXWSHVZSSA6WzfmzNNM&export=download', 'https://drive.google.com/u/0/uc?id=1-_tOr99SVXAR7OH2y3KrjRA4ZJA4IdVf&export=download', 'https://drive.google.com/u/0/uc?id=1uDQZVsOqLws3EUPjkNY6md4LSzAQfOFD&export=download']
output_list = ['yolo.h5', 'yolov3.weights','yolo.py','trained_weights_1915_final.h5']
output_dir = os.path.join(tablext_src_dir,'yolo_helpers','keras_yolo3')
for i in range(len(output_list)):
 	gdown.download(url_list[i], os.path.join(output_dir,output_list[i]), quiet=False)

gdown.download('https://drive.google.com/u/0/uc?id=1uCbQlcQ96Gvm3pjWZFuHZBD9JbmVhzWL&export=download', os.path.join(tablext_src_dir,'yolo_helpers','keras_yolo3','yolo3','model.py'), quiet=False)

print('Cleaning unnecessary files ...')
if os.path.exists(table_extract_robust_zip):
 	os.remove(table_extract_robust_zip)
	
print('Installing necessary python libraries ...')
library_installer("pytesseract")
library_installer("opencv")
library_installer("tensorflow")
library_installer("pdf2image")
print('Initialization has gotten done successfully.')