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
	if py_lib == 'PyPDF2':
		import_name = 'pypdf2'
	elif py_lib == 'pdfminer':
		import_name = 'pdfminer.six'
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

src_dir = os.path.dirname(__file__)

models_url = 'https://drive.google.com/u/0/uc?id=159mK3UpzvMJhDyH0mrjUikXQwT834tYl&export=download'
models_zip = os.path.join(src_dir, 'Models.zip')
if not os.path.exists(models_zip):
	try:
		gdown.download(models_url, models_zip, quiet = False)
		print("File 'Models.zip' downloaded successfully.")
	except Exception as e:
		print(f"Error downloading file 'Models.zip': {e}")
else:
 	print("File 'Models.zip' already exists.")

if not os.path.exists('Models'):
	try:
		os.makedirs('Models')
		print("Directory 'Models' created successfully.")
	except Exception as e:
		print(f"Error creating directory 'Models': {e}")
else:
 	print("Directory 'Models' already exists.")
unpack_archive('Models.zip', os.path.join(src_dir,'Models'), 'zip')

full_dataset_url = 'https://drive.google.com/u/0/uc?id=159mK3UpzvMJhDyH0mrjUikXQwT834tYl&export=download'
full_dataset_zip = os.path.join(src_dir, 'Full_Dataset.zip')
if not os.path.exists(full_dataset_zip):
	try:
		gdown.download(full_dataset_url, full_dataset_zip, quiet = False)
		print("File 'Full_Dataset.zip' downloaded successfully.")
	except Exception as e:
		print(f"Error downloading file 'Full_Dataset.zip': {e}")
else:
 	print("File 'Full_Dataset.zip' already exists.")

if not os.path.exists('Full_Dataset'):
	try:
		os.makedirs('Full_Dataset')
		print("Directory 'Full_Dataset' created successfully.")
	except Exception as e:
		print(f"Error creating directory 'Full_Dataset': {e}")
else:
 	print("Directory 'Full_Dataset' already exists.")
unpack_archive('Full_Dataset.zip', os.path.join(src_dir,'Full_dataset'), 'zip')

print('Cleaning unnecessary files ...')
if os.path.exists(models_zip):
	os.remove(models_zip)
if os.path.exists(full_dataset_zip):
	os.remove(full_dataset_zip)
	
print('Installing necessary python libraries ...')
library_installer("pdfminer")
library_installer("PyPDF2")
library_installer("tensorflow")

print('Initialization has gotten done successfully.')