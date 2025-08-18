#!/usr/bin/python 

import cv2 as cv
import numpy as np

threshold = 200
min_bound_size = 100

def find_pieces_from_image_file(imageFile, imageSize):
    image = cv.imread(imageFile)
    return find_pieces(image, imageSize)

def find_pieces(image, totalSize):
    assert image is not None, "image is not instantiated"

    grey = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
    kernel = np.ones((10,10),np.uint8)

    #handles the dashed lines
    canny_output = cv.Canny(grey, threshold, threshold * 2)
    morph = cv.morphologyEx(canny_output, cv.MORPH_GRADIENT, kernel)
    contours, _ = cv.findContours(morph, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    
    # Find boundries
    contours_poly = [None]*len(contours)
    boundRect = [None]*len(contours)
    for i, c in enumerate(contours):
        contours_poly[i] = cv.approxPolyDP(c, 3, True)
        boundRect[i] = cv.boundingRect(contours_poly[i])

    pieces = get_bounded_areas(contours_poly, boundRect, image, totalSize)
    return pieces


def get_bounded_areas(contours, boundRect, image, totalSize):
    pieces = []
    mask_color = (255, 255, 255)
    blank_image = np.zeros(image.shape[:2], dtype=np.uint8)

    img_h_px, img_w_px, _ = image.shape
    total_w_in, total_h_in = totalSize

    for i in range(len(contours)):
        x,y,w,h = boundRect[i]
        mask = blank_image.copy()
        cv.drawContours(mask, contours, i, mask_color, -1)
        masked = cv.bitwise_and(image, image, mask=mask)
        masked[mask==0] = mask_color
        cropped = masked[y:y+h, x:x+w]
        width_in = (w / img_w_px) * total_w_in
        height_in = (h / img_h_px) * total_h_in
        pieces.append((cropped, (width_in, height_in)))
    return pieces

if __name__ == "__main__":
    image_file = 'testFiles/BodiceDartedSleeved_GH_A0_1105Upton.png'
    image = cv.imread(image_file)
    a0_inches = (33.1, 46.8)
    pieces = find_pieces(image, a0_inches)
    import os
    path, fileName = os.path.split(image_file)
    counter = 1
    for image, _ in pieces:
        pieceFileName = path + "/piece" + str(counter) + "_" + fileName
        cv.imwrite(pieceFileName, image)
        counter += 1
    
