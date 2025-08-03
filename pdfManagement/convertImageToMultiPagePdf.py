#!/usr/bin/python 
from pdf2image import convert_from_path
import cv2 as cv
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
import math
import time

REPORT_LAB_DPI = 72

def divide_image(image, page_size, image_size_inch):
  pages = []
  image_dpi = image.shape[0]/image_size_inch[0]
  conversion_factor = image_dpi / REPORT_LAB_DPI
  page_x = round((page_size[0] * image.shape[0])/(image_size_inch[0] * REPORT_LAB_DPI))
  page_y = round((page_size[1] * image.shape[1])/(image_size_inch[1] * REPORT_LAB_DPI))

  print((page_x, page_y))

  x_page_count = math.ceil(image.shape[0]/page_x)
  y_page_count = math.ceil(image.shape[1]/page_y)

  for x in range(x_page_count):
    x_start = x * page_x
    x_end = x_start + page_x
    for y in range(y_page_count):
      y_start = y * page_y
      pages.append(image[x_start:x_end, y_start:y_start + page_y])

  return pages

def convert_image(numpy_img):
  new_file_name = f"testFiles/tmp_image{time.time()}.png"
  cv.imwrite(new_file_name, numpy_img)
  return new_file_name

def export_multi_page_pdf(image, page_size, image_size_inches):
  print(page_size)
  print(image.shape)

  doc = canvas.Canvas("testFiles/test.pdf", pagesize=page_size)
  split_images = divide_image(image, page_size, image_size_inches)
  for img in split_images:
    file_name = convert_image(img)
    drawn_size = doc.drawImage(file_name, 0, 0, page_size[0], page_size[1])
    # The library will not accept a file in tmp, so this is the work around
    os.remove(file_name)
    doc.showPage()
  doc.save()

if __name__ == "__main__":
  image_file = 'testFiles/BodiceDartedSleeved_GH_A0_1105Upton.png'
  image = cv.imread(image_file)
  a0_inches = (33.1, 46.8)

  from reportlab.lib.pagesizes import letter # Size at 72 DPI
  export_multi_page_pdf(image, letter, a0_inches)

