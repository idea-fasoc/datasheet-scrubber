from Address import Address
import PyPDF2
import re
import os.path

def pdf_cropper(source_path,destination_path,pdf_filename,number_page):
    page_seperated=[]
    PDFfilename = source_path #filename of your PDF/directory where your PDF is stored
    pfr = PyPDF2.PdfFileReader(open(PDFfilename, "rb")) #PdfFileReader object
    if pfr.isEncrypted: #needed for some encrypted files like AD7183
        pfr.decrypt('')
    #page_number= pfr.getNumPages()
    for i in range(0,number_page):
        #page_seperated.append(str(i))
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
        pdfname = pdf_filename.split(".pdf")[0]
        page_name = pdfname + "_" + str(i) + ".pdf"
        NewPDFfilename=os.path.join(destination_path,page_name)#filename of your PDF/directory where you want your new PDF to be
        pg = pfr.getPage(i) #extract pg 1
        writer = PyPDF2.PdfFileWriter() #create PdfFileWriter object
	#add pages
        writer.addPage(pg)
        with open(NewPDFfilename, "wb") as outputStream: #create new PDF
            writer.write(outputStream) #write pages to new PDF
def pdf_cropper_multiple(pdfDir, pageDir):
    for pdf in os.listdir(pdfDir):
        fileExtension = pdf.split(".")[-1]
        if fileExtension == "pdf":
            #source_path
            pdfFilename = os.path.join(pdfDir, pdf)
            #destination_path
            pdfname = pdf.split(".pdf")[0]
            pageFolder = os.path.join(pageDir, pdfname)
            #Counting number of pdf pages
            pfr = PyPDF2.PdfFileReader(open(pdfFilename, "rb"))
            number_page=pfr.getNumPages()
            pdf_cropper(pdfFilename, pageFolder, pdf, number_page)
