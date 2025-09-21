from pypdf import PdfReader, PdfWriter, PageObject, Transformation
import argparse
from pathlib import Path
import shutil

def getSignatureConfig(numPages):
    if numPages < 100:
        return 8, [7, 0, 5, 2, 1, 6, 3, 4]
    else:
        return 16, [15, 0, 13, 2, 1, 14, 3, 12, 11, 4, 9, 6, 5, 10, 7, 8]
    
def addBlankPages(writer, numPages, sigSize, pageWidth, pageHeight):
    pagesNeeded = sigSize - (numPages % sigSize)
    if pagesNeeded != sigSize:
        for i in range(pagesNeeded):
            writer.add_blank_page(pageWidth, pageHeight)

def createSigLayout(inputPath, outputPath):
    reader = PdfReader(inputPath)
    writer = PdfWriter()

    numPages = len(reader.pages)
    sigSize, sigList = getSignatureConfig(numPages)

    firstPage = reader.pages[0]
    pageWidth = float(firstPage.mediabox.width)
    pageHeight = float(firstPage.mediabox.height)

    # add og pages
    for bookPage in reader.pages:
        writer.add_page(bookPage)

    # blank pages to complete signatures
    addBlankPages(writer, numPages, sigSize, pageWidth, pageHeight)

    # write tempnfile
    tempPath = outputPath.with_suffix(".temp.pdf")
    with open(tempPath, "wb") as f:
        writer.write(f)

    # 2nd pass --> reorder signsture
    tempReader = PdfReader(tempPath)
    totalPages = len(tempReader.pages)
    sigWriter = PdfWriter()

    for i in range(0, totalPages, sigSize):
        for j in range(sigSize):
            page_index = i + sigList[j]
            if page_index < totalPages:  # Check bounds
                sigWriter.add_page(tempReader.pages[page_index])

    # write signature ordered pairs
    sigTempPath = outputPath.with_suffix('.sig.temp.pdf')
    with open(sigTempPath, "wb") as f:
        sigWriter.write(f)
    
    # 3rd pass --> create 4-per-page layout
    sigReader = PdfReader(sigTempPath)
    finalWriter = PdfWriter()

    outputWidth = pageHeight * 2
    outputHeight = pageWidth * 2

    # 4-per-page format
    for i in range(0, len(sigReader.pages), 4):
        outputPage = PageObject.create_blank_page(
            width=outputWidth,
            height=outputHeight
        )

        pagesToProcess = sigReader.pages[i:i+4]

        for j, page in enumerate(pagesToProcess):
            row = j // 2
            col = j % 2

            x = pageHeight + pageHeight * row
            y = pageWidth * col

            transformation = (Transformation()
                              .rotate(-270)
                              .translate(x, y))

            outputPage.merge_transformed_page(page, transformation)

        finalWriter.add_page(outputPage)

    # write to output path
    with open(outputPath, "wb") as f:
        finalWriter.write(f)

    # clean temp
    tempPath.unlink(missing_ok=True)
    sigTempPath.unlink(missing_ok=True)

def main():
    parser = argparse.ArgumentParser(description="A script making little books")
    parser.add_argument("--book", help="just book name pdf")
    args = parser.parse_args()

    inputPath = Path(args.book)
    outputPath = Path(f"{inputPath.stem}_littlebook.pdf")

    if not inputPath.exists():
        raise FileNotFoundError(f"{inputPath} doesn't exist")
    
    try:
        createSigLayout(inputPath, outputPath)
        print(f"Created {outputPath}!")
    except Exception as e:
        outputPath.unlink(missing_ok=True)
        raise e

if __name__ == "__main__":
    main()