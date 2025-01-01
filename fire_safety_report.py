from fpdf import FPDF
import pdfkit
# Function to collect data from the user
def collect_data():
    data = {}
    data["Number of floors at ground level and above"] = input("How many floors are there at ground level and above in the building? ")
    data["Number of floors entirely below ground level"] = input("How many floors are entirely below ground level? ")
    data["Floors on which car parking is provided"] = input("Which floors provide car parking? ")
    data["Approximate floor area per floor (m²)"] = input("What is the approximate floor area per floor in square meters? ")
    data["Approximate floor area gross (m²)"] = input("What is the total approximate floor area of the building in square meters? ")
    data["Approximate floor area on ground floor (m²)"] = input("What is the approximate floor area of the ground floor in square meters? ")
    data["Details of construction and layout"] = input("Please describe the construction and layout of the building: ")
    data["Occupancy"] = input("Who occupies the building? (e.g., staff, public) ")
    data["Approximate maximum number of employees at any one time"] = input("What is the approximate maximum number of employees present at any one time? ")
    data["Approximate maximum number of other occupants at any one time"] = input("What is the approximate maximum number of other occupants (e.g., guests, visitors) at any one time? ")
    data["Approximate total number of people present in the building at any one time"] = input("What is the approximate total number of people present in the building at any one time (including employees and other occupants)? ")
    data["Sleeping Occupants"] = input("Who are the sleeping occupants in the building (e.g., guests in rooms)? ")
    data["Disabled employees"] = input("Are there any disabled employees working in the building? If so, how many? ")
    data["Other disabled occupants"] = input("Are there any other disabled occupants (e.g., guests or visitors)? If so, how many? ")
    data["Occupants in remote areas and lone workers"] = input("Are there any occupants in remote areas or lone workers? If so, how many? ")
    data["Young Persons"] = input("Are there any young persons (underage workers or visitors) in the building? If so, how many? ")
    data["Others"] = input("Are there any other specific groups of people in the building? Please specify. ")
    data["Fires in past 10 years"] = input("Have there been any fires in the past 10 years? If so, how many? ")
    data["Cost of Fire Losses"] = input("What is the cost of fire losses (if applicable)? ")
    data["Detail if required"] = input("Please provide any additional details if required. ")
    data["Fire safety legislation"] = input("What fire safety legislation applies to this building (e.g., local regulations or international standards)? ")
    data["Enforced by"] = input("Who enforces the fire safety legislation for this building? ")
    data["Other legislation making significant requirements"] = input("Is there any other legislation that makes significant requirements for fire safety in this building? ")

    return data

# Function to save HTML content to a separate file
def save_html(data):
    # Create the HTML content for the table
    html = """
    <html>
    <head>
        <title>Building Data Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                line-height: 1.6;
            }
            h2 {
                color: #2c3e50;
                text-align: center;
                background-color: #ecf0f1;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #bdc3c7;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th, td {
                border: 1px solid #bdc3c7;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #34495e;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            tr:hover {
                background-color: #f1c40f;
                color: white;
            }
        </style>
    </head>
    <body>
    """
    html += "<h2>General Details</h2>"
    html += "<table>"
    html += "<tr><th>Type</th><th>Values</th></tr>"

    # Add rows for each item in the data
    for key, value in data.items():
        html += f"<tr><td>{key}</td><td>{value}</td></tr>"

    html += "</table>"
    html += "</body></html>"

    # Save the HTML content to a file
    with open("building_data_report.html", "w") as file:
        file.write(html)
    print("HTML file saved as 'building_data_report.html'")

    
# Function to generate the PDF
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16, style='B')  # Title font with bold style

    # Add the Topic as "General Details"
    pdf.cell(200, 10, "General Details", ln=True, align='C')

    pdf.ln(10)  # Add some space after the title
    pdf.set_font("Arial", size=12)  # Reset font for the table content

    # Set the column widths
    col_width = 90  # Adjust the column width as needed

    # Add the table headers with highlighted background
    pdf.set_fill_color(240, 240, 240)  # Light gray background for header
    pdf.cell(col_width, 10, "Type", border=1, align='C', fill=True)
    pdf.cell(col_width, 10, "Values", border=1, align='C', fill=True)
    pdf.ln(10)  # New line after header

    # Add rows for each item in the data
    for key, value in data.items():
        pdf.cell(col_width, 10, key, border=1, align='L')
        pdf.multi_cell(col_width, 10, value, border=1, align='L')  # multi_cell for wrapping long answers
        pdf.ln(5)  # Add space after each row

    # Output the PDF to a file
    pdf.output("building_data_report_with_pdf_table.pdf")
    print("PDF file saved as 'building_data_report_with_pdf_table.pdf'")

def main():
    # Collecting data from the user
    data = collect_data()

    # Generate and save both PDF and HTML files
    save_html(data)
    # generate_pdf(data)




    # Path to wkhtmltopdf executable (update this path if wkhtmltopdf is not in PATH)
    wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

    # Configure pdfkit to use the wkhtmltopdf executable
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    # Convert the HTML file to PDF
    input_file = 'building_data_report.html'  # Ensure this file exists in the same directory or provide the full path
    output_file = 'building_data_report.pdf'  # Desired output PDF file name
    pdfkit.from_file(input_file, output_file, configuration=config)

    print(f"Converted {input_file} to {output_file} successfully!")




if __name__ == "__main__":
    main()
    
