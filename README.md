# FASoC Datasheet-Scrubber
The FASoC Datasheet Scrubbet is a utility that scrubs through large sets of PDF datasheets/documents in order to extract key circuit information. The information gathered is used to build a database of commercial off-the-shelf (COTS) IP that can be used to build larger SoC in the FASoC design. More information [here](https://fasoc.engin.umich.edu/datasheet-scrubber)
You can do Datasheet Scrubbing by running Datasheet_Scrubbing.py, which you can input a datasheet (between one of ADC, CDC, DCDC, PLL, LDO, SRAM, Temperature Sensor categories) and observe the extracted specs and pins. Instruction steps of each of these would be as follows:
### Getting Started
These are steps for compiling codes:
1. Clone the datasheet-scrubber repository
```bash
git clone 
```
2. Go to [here](https://www.dropbox.com/s/ixrf3t2dl1a9p4s/All_pdf.zip?dl=0) and download (All_pdf.zip should be downloaded)

3. Run make init which runs Initializer.py. It will ask you to type All_pdf.zip directory, your work directory, and your code dirrectory (for datasheet scrubbing) that you have just cloned. After running initializer.py you should see something like this.

![](src/docs/fig1.png)

4. All_pdf, All_text, cropped_pdf, and cropped_text are training directories. For addign more files to training set put your labeled pdf files in All_pdf directory (it means put ADC datasheets in ADC folder inside All_pdf, CDC datasheet in CDC folder inside All_pdf and so on).

5. Run make categorizer which runs test_confusion_matrix.py and shows the confusion matrix of our categorizer on whole dataset.

6. Put pdf files of datasheets that you want to test in Test_pdf folder and please email them to fayazi@umich.edu in order to have a better repository.

7. Run make extraction which runs Datasheet_Scrubbing.py which you can input a datasheet (between one of ADC, BDRT, CDC, counters, DAC, DCDC, Delay_Line, Digital_Potentiometers, DSP, IO, LDO, Opamp, PLL, SRAM, Temperature Sensor categories) and observe the extracted specs and pins. 

### Contributing
Extracted datasheets can be emailed to fayazi@umich.edu in order build a bigger repository.
