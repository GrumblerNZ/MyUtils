from pypdf import PdfWriter
import glob

writer = PdfWriter()
for pdf_file in sorted(glob.glob("*.pdf")):  # Adjust pattern if needed
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged_invoices.pdf", "wb") as output:
    writer.write(output)

print("Merged into merged_invoices.pdf")