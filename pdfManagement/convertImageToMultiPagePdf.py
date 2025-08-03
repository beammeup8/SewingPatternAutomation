#!/usr/bin/python 
from pdf2image import convert_from_path
import cv2 as cv
import numpy as np
from reportlab.pdfgen import canvas
from PIL import Image
from io import BytesIO 
from reportlab.lib.utils import ImageReader
import time
import os

REPORT_LAB_DPI = 72
image_count = 0

def divide_image(image, page_size, image_size_inch):
  pages = []
  image_dpi = image.shape[0]/image_size_inch[0]


  return pages
def convert_images(numpy_img):
  new_file_name = f"testFiles/tmp_image_{image_count}.png"
  image_count +=1
  cv.imwrite(new_file_name, numpy_img)
  return new_file_name

def export_multi_page_pdf(image, page_size, image_size_inches):
  page_x, page_y = page_size
  print(page_size)
  print(image.shape)

  doc = canvas.Canvas("testFiles/test.pdf", pagesize=page_size)
  split_images = divide_image(image, page_size, image_size_inches)
  for img in split_images:
    file_name = convert_image(img)
    drawn_size = doc.drawImage(file_name, 0, 0)
    # The library will not accept a file in tmp, so this is the work around
    os.remove(file_name)
    doc.showPage()
    print(drawn_size)
  doc.save()

if __name__ == "__main__":
  image_file = 'testFiles/BodiceDartedSleeved_GH_A0_1105Upton.png'
  image = cv.imread(image_file)
  a0_inches = (33.1, 46.8)

  from reportlab.lib.pagesizes import letter # Size at 72 DPI
  export_multi_page_pdf(image, letter, a0_inches)

