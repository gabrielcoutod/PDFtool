import click
import fitz
from pathlib import Path


@click.group()
def cli():
    pass


@cli.command()
@click.argument('filename')
@click.argument('output')
@click.option('-r', '--page_range', nargs=2, type=click.INT)
@click.option('-n', '--page_numbers', default="")
@click.option('-s', '--separate', is_flag=True, default=False)
def extractpages(filename, output, page_range, page_numbers, separate):
    ''' Extracts pages from a pdf file. Creates a single pdf file with the pages or separate files with each page.'''
    with fitz.open(filename) as doc:

        num_pages = doc.page_count
        pages = get_pages(page_range, page_numbers, num_pages)
        
        if not separate:
            doc.select([page - 1 for page in pages])
            doc.save(output)
        else:
            output = output[:-4] if output[-4:].lower() == ".pdf" else output

            for page in pages:
                with fitz.open() as new_doc:
                    new_doc.insert_pdf(doc, from_page=page - 1, to_page=page - 1)
                    new_doc.save(f"{output}-{page}.pdf")

@cli.command()
@click.argument("files", nargs=-1)
@click.argument("pdf_path")
def image2pdf(files, pdf_path):
    ''' Creates a pdf file from the input images.'''
    with fitz.open() as doc:
        for file in files:
            with fitz.open(file) as image_doc:
                rect = image_doc[0].rect
                pdfbytes = image_doc.convert_to_pdf()
                with fitz.open("pdf",pdfbytes) as imgPDF:
                    page = doc.new_page(width = rect.width, height = rect.height) 
                    page.show_pdf_page(rect, imgPDF, 0)
        doc.save(Path(pdf_path))

@cli.command()
@click.argument("files", nargs=-1)
@click.argument("output")
def mergepdf(files, output):
    '''Merges pdf files into one file.'''
    with fitz.open() as doc:
        for file in files:
            with fitz.open(file) as file_doc:
                doc.insert_pdf(file_doc, from_page=0, to_page=len(file_doc) - 1)
        doc.save(output)

@cli.command()
@click.argument('filename')
@click.argument('output_dir')
@click.option('-r', '--page_range', nargs=2, type=click.INT)
@click.option('-n', '--page_numbers', default="")
def pdf2image(filename, output_dir, page_range, page_numbers):
    ''' Creates images from the pages of the pdf file.'''
    with fitz.open(filename) as doc:
        filename = filename[:-4] if filename[-4:].lower() == ".pdf" else filename

        output_dir = Path(output_dir)

        num_pages = doc.page_count        
        pages = get_pages(page_range, page_numbers, num_pages)
        for i in pages:
            page = doc[i - 1]
            pix = page.get_pixmap()
            pix.save(output_dir / f"{filename}-page-{i}.jpg")

@cli.command()
@click.argument('filename')
@click.argument('output')
@click.option('-r', '--page_range', nargs=2, type=click.INT)
@click.option('-n', '--page_numbers', default="")
def removepages(filename, output, page_range, page_numbers):
    ''' Removes pages from the pdf.'''
    with fitz.open(filename) as doc:
        num_pages = doc.page_count
        pages = get_pages(page_range, page_numbers, num_pages)
        for i in pages:
            doc.delete_page(i - 1)
        doc.save(output)

def get_pages(page_range, page_numbers,  num_pages):
    if page_numbers:
        page_numbers = [int(page_number) for page_number in page_numbers.split(' ')]
    else:
        page_numbers = []

    if len(page_numbers) > 0 and len(page_range) > 0:
        raise click.exceptions.ClickException("page_range and page_numbers were both given as arguments.")
    elif len(page_numbers) > 0:
        pages = page_numbers
    elif len(page_range) > 0:
        pages = range(page_range[0] , page_range[1] + 1)
    else:
        pages = range(1,num_pages+1)
    return [page for page in pages if page >= 1 and page <= num_pages]

if __name__ == '__main__':
    cli()