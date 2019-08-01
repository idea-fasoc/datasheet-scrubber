### Environment

Python 3.7 is required, older versions of Python will not work. You will also need the following Python libraries which can be installed via pip (in PowerShell/terminal).

1. Install and upgrade pip: `python -m pip install --upgrade pip`

2. Install Python dependencies
	```
	pip install pandas
	pip install -U scipy
	pip install matplot
	pip install matplotlib
	pip install pdfminer.six
	pip install pypdf2
	pip install request
	pip install lxml
	pip install tabula-py
	pip install sklearn
	pip install regex
	pip install keras
	pip install tensorflow*
	pip install pdf2image
	pip install pillow
	pip install pytesseract
	pip install -U numpy
	pip install opencv-python
	```
	*If you wish to retrain the CNN it is highly recommended that you install tensorflow-gpu and have a compatible graphics card.
	
3. Install the following software:
     - Poppler
     - Tesseract
     - Visual Studio 2017

### Getting Started

These are steps for compiling codes:
1. Download the code within the Tablext folder and import it into to Visual Studio. ML.py and ML_Table_Extracter are for the main Tablext software and Table_identifier is to retrain the CNN.

2. Download the Setup_Folders within Tablext and change the "Root" variable in both ML_Table_Extracter and Table_identifier to your local Setup_Folders path.

3. From the release tab download the file model_weights.h5 and place it into the "Identifier" folder inside of your "Setup_Folders"

4. Make sure that your ML_Table_Extracter and Table_identifier are set to be the top level code.

5. To run the main program, ML_Table_Extacter input the file you wish to extract in the pdf_file variable, several example files are given in the PDFs folder. it currently is easiest to input a PDF file so if you have an image you wish to extract, first convert it to a PDF file.

6. To run Table_identifier set the rebuild bool to True inorder to rebuild the network and set the reextract bool to True in order to input your own input data

