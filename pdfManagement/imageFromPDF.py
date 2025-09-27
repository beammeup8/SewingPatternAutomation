#!/usr/bin/python 

from pdf2image import convert_from_path

def convert_to_image(pdf_filename):
    images = convert_from_path(pdf_filename)

    file_name_root = pdf_filename[:-4]

    if len(images) != 1:
        counter = 0
        fileNames = []
        for image in images:
            fileName = file_name_root + str(counter) +'.png'
            image.save(fileName, 'PNG')
            fileNames.append(fileName)
            counter += 1
        return fileNames, images
    else:
        fileName = file_name_root +'.png'
        images[0].save(fileName, 'PNG')
        return [fileName], images
    
if __name__ == "__main__":
    filename = "testFiles/output.pdf"
    convert_to_image(filename)
