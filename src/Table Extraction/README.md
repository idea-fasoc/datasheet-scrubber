# Table Extraction

A majority of a datasheet’s relevant specifications are found within their various tables. Our tool identifies the location of tables and extracts information within them.

### Environment Setup

Requirements: Python 3.6/3.7 (packages pytesseract, pdf2image, opencv-python, numpy, keras, tensorflow). Python versions below 3.6 are not supported.

1.  After pulling the table extraction code, download the required neural network models by following the instructions below.

    - Navigate to [here](https://umich.app.box.com/s/64pqr725gbz538q1htgb60x3alrxrkiy).

    - Download the folder "Table_extract_robust" inside the folder "Tablext".
  
2.  Update the "root" variable within Main_code to your local location of "Table_extract_robust." 
  e.g. r"C:/Users/User/Downloads/Table_extract_robust".
  
3. Download [Poppler](https://poppler.freedesktop.org/), and [Tesseract](https://github.com/tesseract-ocr/tesseract/releases/tag/3.05.02). Reference the software in your system variables.
      
4.  Run the code and follow the terminal prompts.
