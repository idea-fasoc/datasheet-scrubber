import os
import pdf_cropper
import pdf_csv_converter
import pdftotext
import PyPDF2
import zipfile

def init_dropbox(main_path):
    print("Extracting All_pdf.zip...")
    zip_file = zipfile.ZipFile(os.path.join(main_path,"All_pdf.zip"),'r')
    zip_file.extractall(main_path)
    print("Extracting All_pdf.zip Complete")
    source_path = os.path.join(main_path,"Test")
    destination_csv_path = os.path.join(main_path, "CSV")
    destination_pdf_path = os.path.join(main_path, "Modified_pdf")
    destination_text_path = os.path.join(main_path, "All_text")
    destination_cropped_pdf_path = os.path.join(main_path, "cropped_pdf")
    destination_cropped_text_path = os.path.join(main_path, "cropped_text")
    New_pdf_path = os.path.join(main_path, "New_pdf")
    Test_pdf = os.path.join(main_path, "Test_pdf")
    Test_text = os.path.join(main_path, "Test_text")
    Test_cropped_pdf = os.path.join(main_path, "Test_cropped_pdf")
    Test_cropped_text = os.path.join(main_path, "Test_cropped_text")


    ##creating the cooresponding folder
    print("Creating folder...")
    if not os.path.exists(destination_csv_path):
        os.mkdir(destination_csv_path)
    else:
        print("ERROR: CSV path already exists")
        return -1
    if not os.path.exists(destination_pdf_path):
        os.mkdir(destination_pdf_path)
    else:
        print("ERROR: Modified pdf path already exists")
        return -1
    if not os.path.exists(destination_text_path):
        os.mkdir(destination_text_path)
    else:
        print("ERROR: All_text path already exists")
        return -1
    if not os.path.exists(destination_cropped_pdf_path):
        os.mkdir(destination_cropped_pdf_path)
    else:
        print("ERROR: cropped_pdf path already exists")
        return -1
    if not os.path.exists(destination_cropped_text_path):
        os.mkdir(destination_cropped_text_path)
    else:
        print("ERROR: cropped_text path already exists")
        return -1
    if not os.path.exists(New_pdf_path):
        os.mkdir(New_pdf_path)
    else:
        print("ERROR: New_pdf path already exists")
        return -1
    if not os.path.exists(Test_cropped_pdf):
        os.mkdir(Test_cropped_pdf)
    else:
        print("ERROR: Test_cropped_pdf path already exists")
        return -1
    if not os.path.exists(Test_cropped_text):
        os.mkdir(Test_cropped_text)
    else:
        print("ERROR: Test_cropped_text path already exists")
        return -1
    if not os.path.exists(Test_pdf):
        os.mkdir(Test_pdf)
    else:
        print("ERROR: Test_pdf path already exists")
        return -1
    if not os.path.exists(Test_text):
        os.mkdir(Test_text)
    else:
        print("ERROR: Test_text path already exists")
        return -1
    print("Creating folder Complete")

    print("Initializing files...")
    for fpath, dirname, fname in os.walk(source_path):
        for files in fname:
            print(files)
            print("--------------------------------------------------------")
            ## creating the empty folder
            category_folder = fpath.split("\\")[-1]
            os.mkdir(os.path.join(New_pdf_path, category_folder))
             ## creating the source path
            source_pdf_path = os.path.join(fpath, files)
            source_csv_path = destination_pdf_path
            ## creating Modified pdf
            print("Creating Modified pdf...")
            last_directory_word_spliting_pdf = source_pdf_path.split(chr(92))
            last_pdf_directory_word = last_directory_word_spliting_pdf[-1]
            last_directory_word_spliting_csv = last_pdf_directory_word.split(".")
            last_csv_directory_word = last_directory_word_spliting_csv[0] + "." + "csv"
            pfr = PyPDF2.PdfFileReader(open(source_pdf_path, "rb"))
            number_page = pfr.getNumPages()  # Counting number of pdf pages
            print("Creating Modified pdf Complete")
            ## creating csv
            # Convert each pdf page to CSV file and save each CSV page separately
            print("Creating CSV...")
            pdf_cropper.pdf_cropper(source_pdf_path, destination_pdf_path, last_pdf_directory_word, number_page)
            pdf_csv_converter.pdf_csv_converter(source_csv_path, destination_csv_path, last_pdf_directory_word,
                                                last_csv_directory_word, number_page)
            print("Creating CSV Complete")
            # creating text
            print("Generating text...")
            os.mkdir(os.path.join(destination_text_path, category_folder))
            final_destination_text_path = os.path.join(destination_text_path, category_folder)
            pdftotext.PDFtoTEXT(source_pdf_path, final_destination_text_path)
            print("Generating text Complete")
            ## creating cropped pdf
            print("Generating cropped pdf...")
            os.mkdir(os.path.join(destination_cropped_pdf_path, category_folder))
            final_destination_cropped_pdf_path = os.path.join(destination_cropped_pdf_path, category_folder)
            pdf_cropper.pdf_cropper_all(source_pdf_path, final_destination_cropped_pdf_path, files, 2)
            print("Generating cropped pdf Complete")
            ## creating cropped text
            print("Generating cropped text...")
            os.mkdir(os.path.join(destination_cropped_text_path, category_folder))
            cropped_text_source = os.path.join(destination_cropped_pdf_path, category_folder, files)
            final_destination_cropped_text_path = os.path.join(destination_cropped_text_path, category_folder)
            pdftotext.PDFtoTEXT(cropped_text_source, final_destination_cropped_text_path)
            print("Generating cropped text Complete")
            print(files, "Complete")

    print("Initializing Complete")

# the input is the source directory of all pdf, it will create modified pdf and csv in the same directory as the source directory
# eg.  init_dropbox(r"D:\All_pdf")
