# FASoC-Datasheet-Scrubber
Thanks for downloading and using our codes. You can do Datasheet Scrubbing by running Datasheet_Scrubbing.py, which you can input a datasheet (between one of ADC, CDC, DCDC, PLL, LDO, SRAM, Temperature Sensor categories) and observe the extracted specs and pins. Instruction steps of each of these would be as follows:

# Datasheet Scrubbing
These are steps for compiling codes:
1. Make a work directory similar to Fig. 1, and write this directory at the first line of Address.txt file (replace the current line of Address.txt, which is C:\Users\morte\Box Sync\Education_tools\project_python_document with your directory.)

 ![](docs/fig1.png)

2. Inside All_pdf, create folders similar to Fig. 2.

 ![](docs/fig2.png)

3. All_pdf, All_text, cropped_pdf, and cropped_text are training directories. For making your training dataset, put your labeled pdf files in All_pdf directory (it means put ADC datasheets in ADC folder inside All_pdf, CDC datasheet in CDC folder inside All_pdf and so on).
4. Open and run make_training_set function to make appropriate files in All_text, cropped_pdf, and cropped_text.
5. Put pdf files of datasheets that you want to test in Test_pdf folder and please email them to fayazi@umich.edu in order to have a better repository.
6. Open and run Datasheet_Scrubbing.py which you can input a datasheet (between one of ADC, CDC, DCDC, PLL, LDO, SRAM, Temperature Sensor categories) and observe the extracted specs and pins. 

**Note: We appreciate if you email your labeled datasheets to fayazi@umich.edu in order to have a better repository.**
