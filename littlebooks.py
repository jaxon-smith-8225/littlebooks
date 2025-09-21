from pypdf import PdfReader, PdfWriter, PageObject, Transformation
import subprocess

def preprocess(pdfPath): 
    # makes sure all pages for signature are present

    reader = PdfReader(pdfPath)
    writer = PdfWriter()

    numPages = len(reader.pages)
    if numPages < 100:
        sigSize = 8
        sigList = [0, 7, 2, 5, 6, 1, 4, 3]
    else:
        sigSize = 16
        sigList = [15, 0, 13, 2, 1, 14, 3, 12, 11, 4, 9, 6, 5, 10, 7, 8]

    firstPage = reader.pages[0]
    pageWidth = float(firstPage.mediabox.width)
    pageHeight = float(firstPage.mediabox.height)

    for bookPage in range(numPages):
        writer.add_page(reader.pages[bookPage])
    for pageNeeded in range(int(sigSize - (numPages % sigSize))):
        writer.add_blank_page(pageWidth, pageHeight) # get up to num of pages to get full signatures
    with open(pdfPath, "wb") as f:
        writer.write(f)
    
    return numPages, sigSize, sigList

def signatureSplitting(inputPath): 
    # splits the pdf into correctly positioned pages for signatures

    numPages, sigSize, sigList = preprocess(inputPath)
    reader = PdfReader(inputPath)
    writer = PdfWriter()

    numPages = len(reader.pages) # update page numbers

    for i in range(0, numPages, sigSize): # there will be i signatures
        lst = sigList
        for j in range(int(sigSize)): # work through signature list
            nextPage = reader.pages[i + lst[j]]
            writer.add_page(nextPage)

    with open(inputPath, "wb") as f:
        writer.write(f)

def fourPerPage(inputPath, scale=1, margin=0): 
    # formats pre-ordered signature pages to be printed

    reader = PdfReader(inputPath)
    writer = PdfWriter()

    numPages = len(reader.pages)

    firstPage = reader.pages[0]
    pageWidth = float(firstPage.mediabox.width)
    pageHeight = float(firstPage.mediabox.height)

    outputWidth = pageHeight * 2 + margin * 3
    outputHeight = pageWidth * 2 + margin * 3

    for i in range(0, numPages, 4):
        outputPage = PageObject.create_blank_page(
            width = outputWidth,
            height = outputHeight
        )

        pagesToProcess = reader.pages[i:i+4]

        for j, page in enumerate(pagesToProcess):

            row = j // 2
            col = j % 2

            x = (pageHeight + margin) + row * (pageHeight)
            y = margin + col * (pageWidth)

            transformation = Transformation().scale(scale, scale).rotate(-270).translate(x, y)

            outputPage.merge_transformed_page(page, transformation)

        writer.add_page(outputPage)

    with open(inputPath, "wb") as f:
        writer.write(f)

if __name__ == "__main__":
    bookName = "EthicsOfAmbiguity" # CHANGE THIS VARIABLE FOR DIFFERENT BOOKS
    littlebookPath = f"{bookName}_littlebook.pdf"

    copyString = f"cp {bookName}.pdf ./{bookName}_littlebook.pdf"
    subprocess.run(copyString)

    signatureSplitting(littlebookPath)
    fourPerPage(littlebookPath)

    print(f"Created {littlebookPath}!")
