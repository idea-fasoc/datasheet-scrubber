# Table Extraction

A majority of a datasheet's relevant specifications are found within their various tables. Our tool identifies the location of tables and extracts information within them.

## Environment Setup

Requirements: [Anaconda](anaconda.com) (Packages: [tesseract](https://anaconda.org/conda-forge/tesseract), [pytesseract](https://anaconda.org/conda-forge/pytesseract), [pdf2image](https://anaconda.org/conda-forge/pdf2image), [opencv](https://anaconda.org/conda-forge/opencv), [keras2.3.1](https://anaconda.org/conda-forge/keras), [poppler](https://anaconda.org/conda-forge/poppler), [matplotlib](https://anaconda.org/conda-forge/matplotlib), [pandas](https://anaconda.org/anaconda/pandas), [numba](https://anaconda.org/numba/numba), [gdown](https://anaconda.org/conda-forge/gdown), [libicinv](https://anaconda.org/conda-forge/libiconv/), [tenserflow2.5.0](https://anaconda.org/conda-forge/tensorflow)).

1. **Create a new Conda environment** with Python 3.8:
   ```bash
   conda create -n <name> python=3.8
   conda activate <name>  
   ```

2. **Install the required packages** in the environment:
   ```bash
   conda install -c conda-forge tesseract pytesseract pdf2image opencv keras2.3.1 poppler matplotlib pandas numba gdown libicinv tensorflow
   ```
3. **Install additional dependencies** in the environment:
   ```bash
   pip install pillow
   ```

 All the required packages will be installed after initializing.

## Troubleshooting Common Errors

1. **ModuleNotFoundError: No module named 'pytesseract'**
   ```bash
   conda install -c conda-forge pytesseract
   ```

2. **ModuleNotFoundError: No module named 'cv2'**
   ```bash
   conda install -c conda-forge opencv
   ```

3. **ModuleNotFoundError: No module named 'tensorflow'**
   ```bash
   conda install -c conda-forge tensorflow=2.5.0
   ```

4. **ImportError: DLL load failed while importing _imaging**
   ```bash
   pip install --upgrade --force-reinstall pillow
   ```

5. **ModuleNotFoundError: No module named 'pdf2image'**
   ```bash
   conda install -c conda-forge pdf2image
   ```

6. **ModuleNotFoundError: No module named 'matplotlib'**
   ```bash
   conda install -c conda-forge matplotlib
   ```

7. **ModuleNotFoundError: No module named 'pandas'**
   ```bash
   pip install pandas
   ```

8. **ModuleNotFoundError: No module named 'numba'**
   ```bash
   conda install -c conda-forge numba
   ```

## Testing
For using the code, you can see [here](https://github.com/idea-fasoc/datasheet-scrubber/tree/master/tests/table_extraction) as an example.
### Test Modes
- `cnn_basic`: Our normal table extraction method which uses CNN
 
- `cnn_advanced`: Our advanced version of table extraction method which uses CNN

- `cnn_yolo`: Applying YOLO to our CNN-based method

### Arguments
- `--pdf_dir`: The directory of the PDF file that you want to extract

- `--work_dir`: The directory that you want to save the results e.g. output CSV file in

- `--first_table_page`: Statring page that you want to extract tables within from your input PDF file

- `--last_table_page`: Last page that you want to extract tables within from your input PDF file

- `--use_yolo`: If it is `True` it means YOLO model would be integrated with our CNN-based model

## Citation
If you find this repo useful in your project or research, please star and consider citing it:

```
@article{colter2022tablext,
  title={Tablext: A Combined Neural Network And Heuristic Based Table Extractor},
  author={Colter, Zach and Fayazi, Morteza and Benameur-El Youbi, Zineb and Kamp, Serafina and Yu, Shuyan and Dreslinski, Ronald},
  journal={Array},
  volume={15},
  pages={100220},
  year={2022},
  publisher={Elsevier}
}
```
