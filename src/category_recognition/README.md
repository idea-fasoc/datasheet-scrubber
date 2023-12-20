# Category Recognition

The first step to automatically scrub datasheets is to recognize the IP category, e.g. ADC, Phase Locked Loop (PLL), etc. This is a crucial point since we should look for different information packages based on the IP category. Categorizing documents helps us to search and find the desired information more precisely and purposefully.

### Environment Setup

Requirements: [Anaconda](anaconda.com) (Packages: [pdfminer.six](https://anaconda.org/conda-forge/pdfminer.six), [keras2.3.1](https://anaconda.org/conda-forge/keras), [tenserflow2.5.0](https://anaconda.org/conda-forge/tensorflow), [PyPDF2](https://anaconda.org/conda-forge/pypdf2)). All the required packages will be installed after initializing.

After pulling the table extraction code, please initialize the environment:
- `cd src/category_recognition`
- `make init`
    
### Testing
For using the code, you can see [here](https://github.com/idea-fasoc/datasheet-scrubber/tree/master/tests/category_recognition) as an example.
### Test Modes
- `single_file`: When the category of only one file needs to be recognized
-  `conf_matrix`: When the category of multiple files needs to be recognized. This option gives the total average accuracy of our model.
