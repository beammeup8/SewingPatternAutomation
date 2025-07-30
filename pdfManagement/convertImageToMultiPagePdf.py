#!/usr/bin/python 
from pdf2image import convert_from_path
import cv2 as cv
import numpy as np
from reportlab.pdfgen import canvas
from PIL import Image
from io import BytesIO 
from reportlab.lib.utils import ImageReader
import time

def divide_image(image, page_size):
  #TODO divide image up into a list of images
  return [image]

def convert_image(numpy_img):
  new_file_name = f"testFiles/image_{time.time()}.png"
  cv.imwrite(new_file_name, numpy_img)
  return new_file_name

def export_multi_page_pdf(image, page_size):
  page_x, page_y = page_size
  print(page_size)
  print(image.shape)

  doc = canvas.Canvas("testFiles/test.pdf", pagesize=page_size)
  split_images = divide_image(image, page_size)
  for img in split_images:
    drawn_size = doc.drawImage(convert_image(img), 0, 0, 1000, 1000)
    doc.showPage()
    print(drawn_size)
  doc.save()

if __name__ == "__main__":
  image_file = 'testFiles/BodiceDartedSleeved_GH_A0_1105Upton.png'
  image = cv.imread(image_file)

  from reportlab.lib.pagesizes import letter # Size at 72 DPI
  export_multi_page_pdf(image, letter)

