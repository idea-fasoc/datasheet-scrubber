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

import argparse  # arguement parsing
import os  # filesystem manipulation
import shutil

# Parse and validate arguments
# ==============================================================================

pyth_dir = os.path.dirname(__file__)

parser = argparse.ArgumentParser(description='Cleaning Table Extractor Tool')
parser.add_argument('--work_dir', required=True, help='main work and output directory')
args = parser.parse_args()

TempImages_dir = os.path.join(args.work_dir, "TempImages")
if os.path.exists(TempImages_dir):
	shutil.rmtree(TempImages_dir)
if os.path.exists(os.path.join(args.work_dir, "concatenate_table.csv")):
	os.remove(os.path.join(args.work_dir, "concatenate_table.csv"))