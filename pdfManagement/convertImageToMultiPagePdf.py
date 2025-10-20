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

def export_multi_page_pdf(image, page_size_inches, image_size_inches, output_file_name):
  page_size = (page_size_inches[0] * REPORT_LAB_DPI, page_size_inches[1] * REPORT_LAB_DPI)
  print(f"Converting image:")
  print(f"\tfrom dpi:({image.shape[0]}, {image.shape[1]}), in: {image_size_inches}")
  print(f"\tto dpi: {page_size}, in: {page_size_inches}")

  usable_width = page_size[0] - 2 * BORDER_POINTS
  usable_height = page_size[1] - 2 * BORDER_POINTS

  doc = canvas.Canvas(output_file_name, pagesize=page_size)
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

  print("Saving pdf to " + output_file_name)
  doc.save()

def inches_from_format_name(format):
   match format:
    case "letter":
      return (8.5, 11)
    case "legal":
      return (8.5, 14)
    case "tabloid":
      return (11, 17)
    case "ledger":
      return (17, 11) 
    case "a0":
      return (33.1, 46.8)
    case "a1":
      return (23.4, 33.1)
    case "a2":
      return (16.5, 23.4)
    case "a3":
      return (11.7, 16.5)
    case "a4":
      return (8.3, 11.7)
    case "a5":
      return (5.8, 8.3)

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser(
    prog='Image to Printable PDF',
    description='Takes an image, the size of the image to be output (in inches) and converts it to a pdf where the pages make up that size'
  )

  parser.add_argument('image', help='Path to the image file to be split up')
  parser.add_argument('--imagesize', '-i', required=True, help='Size of the image in inches. The format should be (width, height), or the name of the page size (letter/a0)')
  parser.add_argument('--pagesize', '-p', default="letter", help='Size of the output pdf in inches. The format should be (width, height), or the name of the page size (letter/a0), the default is "letter"/(8.5,11)')
  parser.add_argument('--output', '-o', help='Output file name, defaults to the original filename with "_split.pdf" appended')

  args = parser.parse_args()

  image = cv.imread(args.image)
  page_size = args.pagesize
  if isinstance(page_size, str):
    page_size = inches_from_format_name(page_size)
  image_size = args.imagesize
  if image_size is None:
    print("Image size is required")
    exit(1)
  elif isinstance(image_size, str):
    image_size = inches_from_format_name(image_size)

  output_file_name = args.output
  if output_file_name is None:
    output_file_name = args.image[:-4] + "_split.pdf"

  export_multi_page_pdf(image, page_size, image_size, output_file_name)

