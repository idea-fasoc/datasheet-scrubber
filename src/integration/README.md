# Integration

The integration part is meant to help integrating the datascrubber with the database. In other words, we will be able to store the output of the datasheet scrubber inside a DB for further use.


## Setup instructions

- Ensure your machine has the correct python version and all of the python modules required to run through the datasheet scrubber
    - General requirements: Anaconda 3 or Python 3.6/3.7 (packages pandas, scipy, matplot, matplotlib, pdfminer.six, pypdf2, request, lxml, tabula-py, sklearn, regex, keras, tensorflow, pdf2image, pillow, pytesseract, numpy, opencv-python, gensim, nltk). Python versions below 3.6 are not supported

    - Integration requirements: packages gdown and download_file_from_google_drive
    
- Follow all instructions listed [here](https://github.com/idea-fasoc/datasheet-scrubber)

## Main script

- `python3 main.py`
    - Model files: tokenizer_long.pickle and TEXT_IDENTIFY_MODEL_long.h5 will be downloaded from UMICH Mbox and added to you current repository
    - PDF datasheet: a message will ask you to provide the path to your PDF in order to apply category recognition and table extraction 
- After step 1, you should be able csv files "concatenate_table*.csv"
- Run the script *csv_cleaning.py*
    - The script will allow to clean up the csv from the table extractor and only keep the elements needed for the database (according to componenets scrapped from Digikey)
    - The script will then insert the clean data into a database (to configure in the python script)
