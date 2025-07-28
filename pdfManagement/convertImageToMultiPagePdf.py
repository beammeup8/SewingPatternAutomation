#!/usr/bin/python 
from pdf2image import convert_from_path
import cv2 as cv
import numpy as np
from reportlab.pdfgen import canvas
from PIL import Image
from io import BytesIO 
from reportlab.lib.utils import ImageReader

def divide_image(image, page_size):
  #TODO divide image up into a list of images
  return [image]

def convert_image(numpy_img):
  return Image.fromarray(numpy_img)

def export_multi_page_pdf(image, page_size):
  page_x, page_y = page_size
  print(page_size)
  print(image.shape)

  doc = canvas.Canvas("testFiles/test.pdf", pagesize=page_size)
  split_images = divide_image(image, page_size)
  for img in split_images:
    doc.drawInlineImage(convert_image(img), page_x, page_y, page_x, page_y)
    doc.showPage()
  doc.save()

if __name__ == "__main__":
  image_file = 'testFiles/BodiceDartedSleeved_GH_A0_1105Upton.png'
  image = cv.imread(image_file)

  from reportlab.lib.pagesizes import letter # Size at 72 DPI
  export_multi_page_pdf(image, letter)

