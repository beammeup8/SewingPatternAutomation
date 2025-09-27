
import cv2 as cv

def output_boxes_on_image(original_image, boundaries, new_file_name):
    drawing = original_image.copy()
    color = (0, 255, 0)
    for x, y, w, h in boundaries:
        cv.rectangle(drawing, (x, y), (x + w, y + h), color, 4)

    cv.imwrite(new_file_name, drawing)

def output_contours_on_image(original_image, contours, new_file_name):
    drawing = original_image.copy()
    color = (0, 255, 0)
    cv.drawContours(drawing, contours, -1, color, 2)
    cv.imwrite(new_file_name, drawing)