# Table Extraction

A majority of a datasheet’s relevant specifications are found within their various tables. Our tool identifies the location of tables and extracts information within them.

## Environment Setup

Requirements: Python 3.6.9 or [Anaconda4.10.1](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html) (Packages: [tesseract](https://anaconda.org/conda-forge/tesseract), [pytesseract](https://anaconda.org/conda-forge/pytesseract), [pdf2image](https://anaconda.org/conda-forge/pdf2image), [opencv](https://anaconda.org/conda-forge/opencv), [keras2.3.1](https://anaconda.org/conda-forge/keras), [poppler](https://anaconda.org/conda-forge/poppler), [matplotlib](https://anaconda.org/conda-forge/matplotlib), [pandas](https://anaconda.org/anaconda/pandas), [numba](https://anaconda.org/numba/numba), [gdown](https://anaconda.org/conda-forge/gdown), [libicinv](https://anaconda.org/conda-forge/libiconv/), [tenserflow2.5.0](https://anaconda.org/conda-forge/tensorflow)). Python versions below 3.6 are not supported.

After pulling the table extraction code, please initialize the environment:

`cd src/table_extraction`

`make init`

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
