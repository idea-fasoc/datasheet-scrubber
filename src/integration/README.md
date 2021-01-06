# Integration

The integration part is meant to help integrating the datascrubber with the db.
In other words, we will be able to store the output of the datasheet scrubber inside a DB for further use.


## Setup instructions

1. Ensure your machine has the correct python version and all of the python modules required to run through the datasheet scrubber. 
    - General requirements: Anaconda 3 or Python 3.6/3.7 (packages pandas, scipy, matplot, matplotlib, pdfminer.six, pypdf2, request, lxml, tabula-py, sklearn, regex, keras, tensorflow, pdf2image, pillow, pytesseract, numpy, opencv-python, gensim, nltk). Python versions below 3.6 are not supported.

    - Integration requirements: packages gdown and download_file_from_google_drive.
    
2. Follow all instructions listed [here](https://github.com/idea-fasoc/datasheet-scrubber)

## Main script

1. run the script *main.py*
    - Model files: tokenizer_long.pickle and TEXT_IDENTIFY_MODEL_long.h5 will be downloaded from UMICH Mbox and added to you current repository
    - PDF datasheet: a message will ask you to provide the path to your PDF in order to apply category recognition and table extraction 
