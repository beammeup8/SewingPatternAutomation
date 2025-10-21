# PDF Management

This directory contains scripts for managing PDF files, and extracting images, Specifically for converting images to multi-page PDFs.

## Convert Image to Multipage PDF

This script takes a large image (such as a sewing pattern or ttrpg map) and splits it into multiple pages in a PDF file. This allows you to print a large image on standard-sized paper (like Letter or A4) and then assemble the pages to recreate the original image at the same scale. It also adds alignment marks and page labels to make assembly easier.

### Usage

```bash
usage: Image to Printable PDF [-h]
                              (--imagedim WIDTH HEIGHT | --imagesize PAPER_SIZE_NAME)
                              [--pagedim WIDTH HEIGHT | --pagesize PAPER_SIZE_NAME]
                              [--output OUTPUT_PATH] [--force]
                              IMAGE_PATH

Takes an image, the size of the image and converts it to a pdf where the pages
tile to create the input image at the same scale as the original.

positional arguments:
  IMAGE_PATH            Path to the image file to be split up

options:
  -h, --help            show this help message and exit
  --imagedim WIDTH HEIGHT, -i WIDTH HEIGHT
                        Size of the image to be output in inches
  --imagesize PAPER_SIZE_NAME, -I PAPER_SIZE_NAME
                        Name of the page size that is the image size
  --pagedim WIDTH HEIGHT, -p WIDTH HEIGHT
                        Size of each page of the output pdf in inches.
  --pagesize PAPER_SIZE_NAME, -P PAPER_SIZE_NAME
                        Size of each page of the output pdf by paper size.
                        Defaults to letter
  --output OUTPUT_PATH, -o OUTPUT_PATH
                        Output file name, defaults to the original filename
                        with "_split.pdf" appended
  --force, -f           Force overwrite of image dimensions, this may result
                        in distorted outputs.

```

### Required Arguments
* \<image_file\>: The path and filename of the image to be converted.
* One of the following to specify the real-world size of the input image:
  * `--imagedim`/`-i` <width> <height>: The width and height of the image in inches (e.g., -i 36 48).
  * `--imagesize`/`-I` <size_name>: The paper size name for the image's dimensions (e.g., -I a0).
  
### Optional Arguments
* One of the following to specify the output page size (defaults to letter):
  * --pagedim/-p <width> <height>: The width and height of the output PDF pages in inches (e.g., -p 8.5 11).
  * --pagesize/-P <size_name>: The paper size name for the output pages (e.g., -P a4).
* --output/-o: The desired path and filename for the output PDF file (e.g., test/output.pdf). If not provided, it defaults to the input image name with _split.pdf appended.
* --force/-f: Forces the script to continue even if the image's aspect ratio doesn't match the provided dimensions. This may cause distortion.

### Supported Paper Size Names
letter, legal, tabloid, ledger, a0, a1, a2, a3, a4, a5

### Examples
1. Convert an A0-sized image to a multi-page PDF with letter-sized pages:
    ``` bash
    python convertImageToMultiPagePdf.py my_pattern.png -I a0 -P letter -o my_pattern_printable.pdf
    ```
1. Convert an image with custom dimensions to A4 pages:
    ``` bash
    python convertImageToMultiPagePdf.py my_map.jpg -i 30 20 --pagesize a4
    ```