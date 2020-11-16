# Table Extraction

A majority of a datasheet’s relevant specifications are found within their various tables. Our tool identifies the location of tables and extracts information within them.

### Environment Setup

Requirements: Python 3.6 (packages pytesseract, pdf2image, opencv-python, numpy, keras, tensorflow). Python versions below 3.6 are not supported.

1.  After pulling the table extraction code, download the required neural network models by following the instructions below.

    - Navigate to [here](https://umich.app.box.com/s/64pqr725gbz538q1htgb60x3alrxrkiy).

    - Download the folder "Table_extract_robust" inside the folder "Tablext".
  
2.  Update the "root" variable within Main_code to your local location of "Table_extract_robust." 
  e.g. r"C:/Users/User/Downloads/Table_extract_robust".
  
3. Download [Poppler](https://poppler.freedesktop.org/), and [Tesseract](https://tesseract-ocr.github.io/tessdoc/Home.html). Reference the software in your system variables.
      
4.  Run the code and follow the terminal prompts.

5. If using the combined yolo/cnn detection model, please clone [keras-yolo3](https://github.com/qqwweee/keras-yolo3) or simply write 
    ```bash
   git clone git@github.com:qqwweee/keras-yolo3.git
    ```
    Then download the following three files and add them to keras_yolo3 directory.
     - [yolo.h5](https://drive.google.com/file/d/1jo1KO_DW2ifGaaX_o4jOrbGV-g6bouQL/view?usp=sharing)
     - [yolov3.weights](https://drive.google.com/file/d/1DVVlHgmebYInJE7Gyj58fqWq-NVL8RsH/view?usp=sharing)
     - [yolo.py](https://drive.google.com/file/d/1QTo0anpbvmxd0sNBdNyv-Ld30iDvyxmY/view?usp=sharing)
     
    Add the keras_yolo3 directory to the yolo_helpers directory

    Next, download the [weights](https://drive.google.com/file/d/11Gx_LFV3YlbU2ui7uLOiNqFJkujommzD/view?usp=sharing) for the yolo model and add their path with the command line option --yolo_model path/to/yolo/weights.
