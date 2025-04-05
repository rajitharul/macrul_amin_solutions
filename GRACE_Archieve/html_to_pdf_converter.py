import pdfkit

# Path to wkhtmltopdf executable (update this path if wkhtmltopdf is not in PATH)
wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

# Configure pdfkit to use the wkhtmltopdf executable
config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

# Convert the HTML file to PDF
input_file = 'building_data_report.html'  # Ensure this file exists in the same directory or provide the full path
output_file = 'building_data_report.pdf'  # Desired output PDF file name
pdfkit.from_file(input_file, output_file, configuration=config)

print(f"Converted {input_file} to {output_file} successfully!")
