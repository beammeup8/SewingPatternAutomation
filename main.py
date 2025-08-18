#!/usr/bin/python 
import os

from pdfManagement.imageFromPDF import convert_to_image
from pdfManagement.convertImageToMultiPagePdf import export_multi_page_pdf
from visionComponents.getIndividualPieces import find_pieces_from_image_file
from reportlab.lib.pagesizes import letter

def runProcessing(dirPath):
  files = filter(lambda x: x.endswith(".pdf"), os.listdir(dirPath))
  imageFiles = []
  images = []
  for pdfFileName in files:
    imageFile, image = convert_to_image(dirPath + "/" + pdfFileName)
    imageFiles.extend(imageFile)
    images.extend(image)
  
  print(imageFiles)
  
  pieces = []

  for imageFile, size in imageFiles:
    pieces.extend(find_pieces_from_image_file(imageFile, total_size))

  for image in pieces:
    export_multi_page_pdf(image, letter, size)


runProcessing("testFiles")