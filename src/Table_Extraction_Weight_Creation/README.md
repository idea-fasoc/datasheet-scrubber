### Environment Setup

Requirements: Python 3.6 (packages pytesseract, pdf2image, opencv-python, numpy, keras, tensorflow). Python versions below 3.6 are not supported.

1.  After pulling the table extraction code, download the training data, by following the instructions below, and update the root variable in codes that you use.

    - Navigate to [here](https://umich.app.box.com/s/64pqr725gbz538q1htgb60x3alrxrkiy).

    - Download the folder "Table_extract_robust" inside the folder "Tablext".
    
    
### Code Overview

table_extracter_training_data_checker:			
  Shows the bounding box from the raw xml data on the image

Table_Extracter_robust:					
  Processes the training data into a usable format

Table_Extracter_robust_row 	(NOT USED CURRENTLY):
  Identifies the locations of all rows within a table, needs more training data to be accurate

Table_extracter_robust_concatenate:			
  Creates the model that can concatenate two cells over a vertical line also creates the model that identifies data within the cells

table_identification_final_2.py				
  Creates 2 models that together identify the location of a table on a page
