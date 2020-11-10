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
# 
#importing the scripts to run by the scheduler


######SCRIPT UNDER CONSTRUCTION#######


import sys

from PyPDF2 import PdfFileReader
from subprocess import call
import importlib.util
import gdown
from download_file_from_google_drive import download_file_from_google_drive

url_model1 = 'https://dl.boxcloud.com/d/1/b1\u0021cbmV3AWQI4lYZDx6tjGkIE76lUoHR0W5TnWqS-B22YBF1jXxykgOcJlSasyx5IAkGqWq2jnFfpwYrgh3lN4flctY9qtVgnR5fTnie4AFEH0Uc4VQY8QwEddVpCTK6_18fOa7Wq1pVBEPfi20Bci-NITubss4ze9ucrq6-UH7jldKfVJZ4jPDQWCXr-HVTvK7mSN3yyU6e8XV8Kal2i-z5hPte9nlLFr_2h1zRI2fb3fu5-9E7KgQ-HN7qFQ7EPLuXg6_rz0JJ6r0O5XelF0D5AgA1S_mClYDt7e52uTXkExv-AvUPd9TkLOvDWVeG1CaY5JlE7IAxpbsY29T46paoioTXmBR6NEweMOF0YRrJq4Yk2hgMxwPWB2WJ2JrKfiNNQwVOdtPU4Z5JJARsKlLLolyGc9DTWdlq9y2cl9x6h5azdnp724ogpHLymI_T8agbfNsLfn_9QSveyi69xh8PNvzeKoJ_i6tS1J9zab2IFYUVCs080_B7qeMXlHoVYXNSmbAT0Q8LftbjgOduBTyaOFbSpgY93r3FaTNGJJ8Y2b2dSCr2_JNuXDR6kyGiGlmDRS7d6tyMfmfgJCrVjkjNY335MHI1S4m5bbojEWzHLh4f1ROJffP8ks9U4t2lhESzbsKPu80wDoE8yGeAN0fblxKXpuanrHi2WO2FTpWe-rzqmi8t2TQWAfRW0u172MHWf45MZCLJ7J2bm1_qqpo6anNq-zKrq8tqmrfRSXk-aMPHzcAqn8pLloc4snx2U0vrVQekDO9KreuttadVTTN3waKOoE9-Ue9KoRBAcdVYxi7yWF1GO01EQc374_zKCVMdLcX9FcHZqx8W1q6kADQPrFkZeBqKJYrs7HCZCtKthhWq7KSqaS332x3C1ITUFCJR8hwyPrWiR94vxxjcMyTfxSklrOlzDYwmmnjayNQOEpRkWOsA8QHZH3VlrKBhW4HmNyd2TA4k9om7oF3Rlbs_e8PAYIGS9kPz9TtGc5e2MgdPodEVJta6gX6fwcSPHuqGZwBPx9dfbFIcbG4k9ZKjvIEokGHeeErJBSGTk3W9aum4PE9ltHjh-o67cPG57cgKZV_nG65khBL7Ubd6yI3KSBvxpC-8g4IcgBDSSBYpAXlQUb4hrD6MiT2MpW36Aq3tBm3klBaO1lIvCrvv-CqesCBRunV6121QL3uxTlKROX4L9HseAHCoCONHPDE0bC2c8QEvJMpy8FB1E3DBFOT8a6LCdOg7YgYt19wf8JT3oucSj2Vneh1dIkmEz63Gxarp5Nqgq5Y4sahvBNZyaQubGM45i9QryP7nY0jcH9MCn_Gd51tNFDSl8VCoamvfK-U9Y7RlkB7d_nMkltl_FE-qXSUdN-AZKh1PQ3LQB8K7VWOMxvnYTUy310b0_nKNGZTDbTwZ4ny7JqvX8SA-NNY/download'
output = 'TEXT_IDENTIFY_MODEL_long.h5'
gdown.download(url_model1, output, quiet=False) 
print("EXT_IDENTIFY_MODEL_long.h5 was succesfully downloaded")


#url_model2 ="https://umich.box.com/s/tbby5r2xrck10hnd0z9hzmnx60l3e8c1"



url_model2='https://dl.boxcloud.com/d/1/b1\u00218JKQhYakXua_rAYAdC0JXBt6uiaA_-PYbz7lcQWKEZJFFT7jIgrI1ToHkqCTf-gvBQxM5_sUbcqzcUfEB1TJXMd_pGUVY3gTXb1EmUyQHheOEhTOSs80FI_gp-mdLX3bFnti7c75f8ua-RaP63NAiBwdZOhtRPfgP44AaZm30k0sUIhUdqBVjEEq_J09TeUBqpiC5pZP2-1zFE0bo_WWZbSGVDuN7MDNL_zptqBOnG1mVLLimd_DC1sS5tR9AYzAWRPA7FrCJxzojU9ehRHcba2e7nLS-sw15E9hXt-ytFOpwDRzJ8Y6O_ldfIw0XoZH7fuJltnyvOwkR-DlKgbwLTUCpo61VRHZYarviY2Gb8a5ZBUWiAcHY2ZkNDusr3oK1PDuOzii7PK-xLN3fKB2dJqDO8vJ9cQDF238-XVBGES1uqik8t0pvcTuXWAj--pqu3dYM4ioVeNLQ9mabgNv6M_R8Jp337GUfRfq_RHA84sP-lGu7aaTGbAfSWaxIPDjLYBZbhHV5H19Ojf3oSE3Jx_t9d14s4bNXsGMh94bo97F37mqdLKrPQXURktXaNFkGo8Jo_qXEO1ECy36IuPVZap0tNVpFPNQWF00EroJWFO_kIogsA1T3ojhMhADLxuLXqlV87IchEWfp-9NYtWbC4_3ReYymeGG1IIyf4v7DOmQO_WgMRFYaLnU0FrwL0wO-M1lss7rI4b-yT6Xe8PlXDX7m3THHxwiVXZGp2r0ylJPYSzha5m55P_VNWFfNxTRecUurmxpWx83ABUcqITqyoiimuQgHsAkrtJ-DOgwBcQU3trpwO0Au4AVtiNOKYd4es7XCOJgOP0mZrki9F0kYDqQhOiXwVGLlNgYnY8f3wBQhQaY1jC1P46lhRGKiRABgglYG7qSVgzYdViWaNn-RAphE64xwsTFw3jgoh6OQX4AmSM4SfWMGRBUnrBtrgub3ZOwHePNiZYDiVLG3TD5MeT7NGQE5nHYGWoodim7F5ZTNa1MbQW2K-IiGFZ-wMduaLuFJV8rLhol_cFsZvHkMuwqafFWLue92lLeu5Ocsr1tTZQ2a5d5a4nclY8m5Jrpp20_Bo2GqYR69Z8PygfG05zUyKZd4UuAOIgKabKDJzZoX9nBj7Sgvczxlr6EsV5jHWmxOdpXDiLvO4CWqy0_VJpXffiIGNqoSJdf7Aqo4CvZbCjlYAwjw9Cl7aQp-X38Oe551ykHsqxwq3VD75EklGlqy3i6A8ljr_XGhIgZTEbtdusYxjyBiQr-4KZJ1JyEHab2ldKmLaDwN0i5OPaZGQQ39PDobNI7D7b_H1-l-BwghCneHPoJbrSb1DjIZq7rJHzy952nKQQ3CVpkjnjjx59RC-aK-0SL9kKfGCqb-iDCARGhGlVEcl0B-NQM94KmM7D6knqGZA../download'
output = 'tokenizer_long.pickle'
gdown.download(url_model2, output, quiet=False)

print("okenizer_long.pickle was succesfully downloaded") 


""" file_id1 = 'bchj5h09tjtes6gyhbmosz6w7a15ehfv'
destination1 = '/Users/zinebbenameur/clean/datasheet-scrubber/TEXT_IDENTIFY_MODEL_long.h5'
download_file_from_google_drive(file_id1, destination1)

file_id2 = 'tbby5r2xrck10hnd0z9hzmnx60l3e8c1'
destination2 = '/Users/zinebbenameur/clean/datasheet-scrubber/tokenizer_long.pickle'
download_file_from_google_drive(file_id2, destination2) """



#folder_id = d4ls6xf1x6v2dvnvgzd307pppekrl6sp

#pdf_location = str(sys.argv[1])


def announce():
    print("Imported!")

#get module for python file, this is for the wrapper
def module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

#call the module
wrapper = module_from_file("category_recognizer", "/Users/zinebbenameur/clean/datasheet-scrubber/src/category_recognition/category_recognizer.py")

#Get number of pages from wrapper module
pdf = wrapper.get_number_pages()
number_pages= pdf.getNumPages()

first_page = 1
last_page = number_pages

arguments_weights= "--weight_dir /Users/zinebbenameur/Desktop/datasheet-scrubber/src/Table_extract_robust "
arguments_pdf = "--pdf_dir /Users/zinebbenameur/Desktop/datasheet-scrubber/tests/table_extraction/test.pdf "
arguments_dir = "--work_dir ./ "
argument_pages = "--first_table_page "+ str(first_page)+" --last_table_page "+str(last_page)

#build arguments for table extraction
argumets= arguments_weights + arguments_pdf + arguments_dir + argument_pages
#call table extraction
call("python3 /Users/zinebbenameur/Desktop/datasheet-scrubber/src/table_extraction/table_extraction.py"+" "+argumets, shell=True)
