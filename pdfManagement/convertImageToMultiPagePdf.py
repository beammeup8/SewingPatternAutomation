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
ALIGNMENT_MARK_LEN = 6
LABEL_FONT_SIZE = 18

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
        y_size = y_end - y_start
        for x in range(x_page_count):
            x_start = x * page_width_px
            x_end = min(x_start + page_width_px, img_width_px)
            pages.append((image[y_start:y_end, x_start:x_end],(x_end-x_start, y_size)))

    return pages, x_page_count, y_page_count


def convert_image(numpy_img):
  new_file_name = f"testFiles/tmp_image{time.time()}.png"
  cv.imwrite(new_file_name, numpy_img)
  return new_file_name

def add_page_markings(doc, page_label, usable_width, usable_height, page_size):
   # Draw border rectangle
    doc.setStrokeColorRGB(0, 0, 0)
    doc.setLineWidth(2)
    doc.rect(BORDER_POINTS, BORDER_POINTS, usable_width, usable_height)

    x_mid = BORDER_POINTS + usable_width / 2
    y_mid = BORDER_POINTS + usable_height / 2

    doc.saveState()
    doc.setFont("Helvetica-Bold", LABEL_FONT_SIZE)
    doc.setFillColorRGB(0.85, 0.85, 0.85)

    # Draw alignment marks
    # Top center
    top_edge_y = page_size[1] - BORDER_POINTS
    doc.line(x_mid, top_edge_y - ALIGNMENT_MARK_LEN, x_mid, top_edge_y + ALIGNMENT_MARK_LEN)
    doc.drawCentredString(x_mid, top_edge_y + ALIGNMENT_MARK_LEN + LABEL_FONT_SIZE/2, page_label)
    
    # Bottom center
    doc.line(x_mid, BORDER_POINTS - ALIGNMENT_MARK_LEN, x_mid, BORDER_POINTS + ALIGNMENT_MARK_LEN)
    doc.drawCentredString(x_mid, BORDER_POINTS - ALIGNMENT_MARK_LEN - LABEL_FONT_SIZE, page_label)
    
    # Left center
    doc.line(BORDER_POINTS + ALIGNMENT_MARK_LEN, y_mid, BORDER_POINTS - ALIGNMENT_MARK_LEN, y_mid)
    doc.drawCentredString(BORDER_POINTS - LABEL_FONT_SIZE, y_mid, page_label)

    # Right center
    right_edge_x = page_size[0] - BORDER_POINTS
    doc.line(right_edge_x - ALIGNMENT_MARK_LEN, y_mid, right_edge_x + ALIGNMENT_MARK_LEN, y_mid)
    doc.drawCentredString(right_edge_x + LABEL_FONT_SIZE, y_mid, page_label)


    doc.restoreState()

def export_multi_page_pdf(image, page_size, image_size_inches, outputFileName):
  print(page_size)
  print(image.shape)
  usable_width = page_size[0] - 2 * BORDER_POINTS
  usable_height = page_size[1] - 2 * BORDER_POINTS

  doc = canvas.Canvas(outputFileName, pagesize=page_size)
  split_images, pages_x, pages_y = divide_image(image, (usable_width, usable_height), image_size_inches)
  
  current_page_x = 0
  current_page_y = 0
  current_letter = letters[current_page_y]

  for img, size in split_images:
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

    doc.drawImage(file_name, BORDER_POINTS, BORDER_POINTS, usable_width, usable_height, showBoundary=True, preserveAspectRatio=True)
    add_page_markings(doc, f"{current_letter}{current_page_x}", usable_width, usable_height, page_size)
    
    # The library will not accept a file in tmp, so this is the work around
    os.remove(file_name)
    doc.showPage()
  doc.save()

if __name__ == "__main__":
  image_file = 'testFiles/hartholme.png'
  image = cv.imread(image_file)
  a0_inches = (33.1, 46.8)
  big_square = (37.034, 36)

  from reportlab.lib.pagesizes import letter # Size at 72 DPI
  export_multi_page_pdf(image, letter, big_square, "testFiles/hartholme.pdf")

