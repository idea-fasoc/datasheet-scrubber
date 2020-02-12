# Category Recognition

The first step to automatically scrub datasheets is to recognize the IP category, e.g. ADC, Phase Locked Loop (PLL), etc. This is a crucial point since we should look for different information packages based on the IP category. Categorizing documents helps us to search and find the desired information more precisely and purposefully.

### Environment Setup

Requirements: Python 3.6/3.7 (packages pdfminer.six, numpy, keras, tensorflow). Python versions below 3.6 are not supported.


After pulling the table extraction code, download the required neural network models by following the instructions below.

    - Navigate to [here](https://umich.app.box.com/s/64pqr725gbz538q1htgb60x3alrxrkiy)
    
    - Download the folder "Models" inside the folder "PDF_IDEN"
    
    - Update the "model_location" and "tokenizer_location" variables within the wrapper.
    Additionally, enter the location of the PDF you wish to identify.
