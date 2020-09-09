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
  Creates the model that identifies if data exists within the cells
  
Table_extracter_robust_concatenate_conc:			
  Creates the model that can concatenate two cells over a vertical line

table_identification_final_2.py				
  Creates 2 models that together identify the location of a table on a page
  

  ### YOLO Table Detection
 
To use YOLOv3 backend for table detection (precision/recall is 0.94)
1. fork or clone [this repository](https://github.com/serafibk/TrainYourOwnYOLO)
2. download weights trained from 1915 table images [here](https://drive.google.com/file/d/11Gx_LFV3YlbU2ui7uLOiNqFJkujommzD/view?usp=sharing)
3. navigate to TrainYourOwnYOLO/3_Inference and run:
    ```bash
    python3 Detector.py --input_path path/to/image --output path/to/output/results --yolo_model path/to/downloaded/weights --postfix "_table"
    ```
4. to see results, navigate to TrainYourOwnYOLO/Data/Source_Images and update yolo_results.sh to match:
    ```bash
    python3 show_results.py -y path/to/Detection_Results.csv -t path/to/images/from/detection -x path/to/test/xmls
    ```
    then run (uncomment indicated lines in combined_models.py to see results on test images):
    ```bash
    ./yolo_results.sh
    ```
5. alternatively, to use combined method of current cnns+yolo, instead of step 4, navigate to TrainYourOwnYOLO/Data/Source_Images and update detect_tables.sh to match:
    ```bash
    python3 combined_models.py -c path/to/cnn/models -y path/to/yolo/csv/resutls -t path/to/test/images -x path/to/corresponding/test/xmls
    ```
    then run (uncomment indicated lines in combined_models.py to see results on test images):
    ```bash
    ./detect_tables.sh
    ```

Train and test set available here:
    [Train Images](https://drive.google.com/file/d/1zXsip-MMbtssoSy7HAyofkWO2ILKbpo1/view?usp=sharing)
    [Train Xmls](https://drive.google.com/file/d/1lXgIeh4Qs9-nuBGa-Q5hWKoBli-DH6YC/view?usp=sharing)
    [Test Images](https://drive.google.com/file/d/1DZkWBV3eXbKyaiPU_VJlOc6guEq-pLFE/view?usp=sharing)
    [Test Xmls](https://drive.google.com/file/d/1a6yQBZFmd-47IWjY_UGIU2qrh_SV0Ysx/view?usp=sharing)
 
To retrain with new data, follow the format of the xml files, then perform the following steps:
1. make sure training images are in Training_Images and vott-csv-export folders
2. navigate to TrainYourOwnYOLO/Data and update root and xml folder variables in create_labels.py with path to xml files and run
    ```bash
    python3 create_labels.py
    ```
3. make sure the Annotations-export.csv file is in the vott-csv-export folder then navigate to TrainYourOwnYOLO/1_Image_Annotation and run
    ```bash
    python3 Convert_to_YOLO_format.py
    ```
4. navigate to TrainYourOwnYOLO/2_Training and run 
    ```bash 
    python3 Download_and_Convert_YOLO_weights.py
    ```
5. update hyper parameters if desired with 
    ```bash 
    python3 Train_YOLO.py -h
    ```
    then run
    ```bash 
    python3 Train_YOLO.py
    ```
