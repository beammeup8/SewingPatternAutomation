#!/usr/bin/python 
import os

from pdfManagement.imageFromPDF import convert_to_image
# from pdfManagement.convertImageToMultiPagePdf import getPageBoundaries
from visionComponents.getIndividualPieces import find_pieces_from_image_file

def runProcessing(dirPath):
  files = filter(lambda x: x.endswith(".pdf"), os.listdir(dirPath))
  imageFiles = []
  images = []
  for pdfFileName in files:
    imageFile, image = convert_to_image(dirPath + "/" + pdfFileName)
    imageFiles.extend(imageFile)
    images.extend(image)
  
  print(imageFiles)
  
  for imageFile in imageFiles:
    pieces = find_pieces_from_image_file(imageFile)

  for image in images:
    # TODO split pieces into multiple pages that are printable
    # bounds = getPageBoundaries(image)
    pass


runProcessing("testFiles")