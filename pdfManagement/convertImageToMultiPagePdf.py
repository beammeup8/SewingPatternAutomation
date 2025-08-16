#!/usr/bin/python 
from pdf2image import convert_from_path
import cv2 as cv
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
import math
import time
from string import ascii_uppercase as letters

REPORT_LAB_DPI = 72
BORDER_INCHES = 0.5
BORDER_POINTS = int(BORDER_INCHES * REPORT_LAB_DPI)

def divide_image(image, page_size, image_size_inch):

    img_height_px, img_width_px, _ = image.shape
    img_width_in, img_height_in = image_size_inch[0], image_size_inch[1]

    # Calculate pixels per inch for the image
    pixels_per_inch_x = img_width_px / img_width_in
    pixels_per_inch_y = img_height_px / img_height_in

    # Convert PDF page size from points to inches
    page_width_in = page_size[0] / REPORT_LAB_DPI
    page_height_in = page_size[1] / REPORT_LAB_DPI

    # Calculate how many pixels fit on one PDF page
    page_width_px = round(page_width_in * pixels_per_inch_x)
    page_height_px = round(page_height_in * pixels_per_inch_y)

    x_page_count = math.ceil(img_width_px / page_width_px)
    y_page_count = math.ceil(img_height_px / page_height_px)

    pages = []
    for y in range(y_page_count):
        y_start = y * page_height_px
        y_end = min(y_start + page_height_px, img_height_px)
        for x in range(x_page_count):
            x_start = x * page_width_px
            x_end = min(x_start + page_width_px, img_width_px)
            pages.append(image[y_start:y_end, x_start:x_end])

    return pages, x_page_count, y_page_count


def convert_image(numpy_img):
  new_file_name = f"testFiles/tmp_image{time.time()}.png"
  cv.imwrite(new_file_name, numpy_img)
  return new_file_name

def export_multi_page_pdf(image, page_size, image_size_inches):
  print(page_size)
  print(image.shape)
  usable_width = page_size[0] - 2 * BORDER_POINTS
  usable_height = page_size[1] - 2 * BORDER_POINTS

  doc = canvas.Canvas("testFiles/test.pdf", pagesize=page_size)
  split_images, pages_x, pages_y = divide_image(image, (usable_width, usable_height), image_size_inches)
  
  current_page_x = 0
  current_page_y = 0
  current_letter = letters[current_page_y]

  for img in split_images:
    if current_page_x > pages_x - 1:
       current_page_x = 1
       current_page_y += 1
       if current_page_y > len(letters):
          wrap_count = current_page_y / len(letters)
          current_letter = letters[wrap_count - 1] + letters[current_page_y % len(letters)]
       else:
          current_letter = letters[current_page_y]

    else:
       current_page_x += 1

    file_name = convert_image(img)
    doc.setStrokeColorRGB(0, 0, 0)
    doc.setLineWidth(2)
    doc.rect(BORDER_POINTS, BORDER_POINTS, usable_width, usable_height)
    doc.drawImage(file_name, BORDER_POINTS, BORDER_POINTS, usable_width, usable_height)
    # The library will not accept a file in tmp, so this is the work around
    os.remove(file_name)
    doc.showPage()
  doc.save()

if __name__ == "__main__":
  image_file = 'testFiles/output.png'
  image = cv.imread(image_file)
  a0_inches = (33.1, 46.8)

  from reportlab.lib.pagesizes import letter # Size at 72 DPI
  export_multi_page_pdf(image, letter, a0_inches)

