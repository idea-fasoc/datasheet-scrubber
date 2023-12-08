# Source Codes

The source code of our modules can be found here.

 - [Category-Recognition](https://github.com/idea-fasoc/datasheet-scrubber/tree/master/src/category_recognition): Recognizing the category of datasheet e.g. ADC, PLL, etc.
 - [Table Extraction](https://github.com/idea-fasoc/datasheet-scrubber/tree/master/src/table_extraction): Identifying the tables and extracting information within them. These information are mostly specifications of the datasheets such as INL for ADC or nominal frequency for PLL.
 - [Text Extraction](https://github.com/idea-fasoc/datasheet-scrubber/tree/master/src/text_extraction): Extracting information within text. These information are mostly specifications of the datasheets such as INL for ADC or nominal frequency for PLL.
 - [Database](https://github.com/idea-fasoc/datasheet-scrubber/tree/master/src/database): The entire collection of components of the "IC" category in the Digikey that we have used for training our model.
 - [Integration](https://github.com/idea-fasoc/datasheet-scrubber/tree/master/src/integration): Integrating all the modules into one platform.
 
 If a new datasheet has been input to our scrubber, after recognizing the category, the specifications will be extracted by the table and text extractors and it will be added to the database. 
 
 ![](docs/flow.jpg)
