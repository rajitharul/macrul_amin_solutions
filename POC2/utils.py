from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import reportlab
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from PIL import Image, ImageDraw, ImageFont
import os

import platform
def reference_images_to_pdf(form_id):
    # Path to the folder containing images
    image_folder = f"uploads/{form_id}"
    
    # Output PDF path
    output_pdf_path = f"downloads/reference_pictures_{form_id}.pdf"
    
    # Ensure downloads directory exists
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
    
    # Create PDF canvas
    c = canvas.Canvas(output_pdf_path, pagesize=A4)
    width, height = A4
    
    # Calculate image size (1/3rd of A4 width)
    img_size = width / 3
    
    # Margins and padding
    margin_x = inch  # Left and right margins
    margin_y = 0.5 * inch  # Reduced top and bottom margins
    vertical_padding = 0.5 * inch  # Space between rows of images
    horizontal_padding = 0.5 * inch  # Space between columns of images
    
    # White background
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Header for Reference Images
    c.setFillColorRGB(0.2, 0.2, 0.2)  # Dark gray
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height - margin_y, "Reference Images")
    
    # Get list of image files
    image_files = [f for f in os.listdir(image_folder) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    
    # Track vertical position and page number
    y_position = height - margin_y - 1.5*inch
    page_number = 1
    x_positions = [
        margin_x, 
        margin_x + img_size + horizontal_padding, 
        margin_x + 2*(img_size + horizontal_padding)
    ]
    current_column = 0
    
    # Add images to PDF
    for filename in image_files:
        # Full path to image
        image_path = os.path.join(image_folder, filename)
        
        # Open image to get dimensions
        img = Image.open(image_path)
        img_width, img_height = img.size
        
        # Calculate scaled image size maintaining aspect ratio
        aspect_ratio = img_height / img_width
        scaled_height = img_size * aspect_ratio
        
        # Check if we need a new page
        if y_position - scaled_height < margin_y:
            c.showPage()
            page_number += 1
            y_position = height - margin_y - 1.5*inch
            current_column = 0
        
        # Draw image
        c.drawImage(image_path, x_positions[current_column], y_position - scaled_height, 
                    width=img_size, height=scaled_height)
        
        # Move to next column/row
        current_column += 1
        if current_column > 2:
            current_column = 0
            y_position -= scaled_height + vertical_padding
    
    # Save PDF
    c.save()
    
    return output_pdf_path

def generate_cover_pdf(form_id, property_name):
    # Create download/property_cover_page directory if it doesn't exist
    cover_page_dir = os.path.join("downloads", "property_cover_page")
    os.makedirs(cover_page_dir, exist_ok=True)
    
    # Define PDF path in the new directory
    pdf_path = os.path.join(cover_page_dir, f"cover_{form_id}.pdf")
    
    # Create canvas
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # Background color
    c.setFillColorRGB(1, 1, 1)  # White background
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Company Header (bright red color)
    c.setFillColorRGB(1, 0.192, 0.192)  # Bright red color (#FF3131 in RGB)
    c.setFont("Helvetica-Bold", 24)  # Larger font size
    c.drawCentredString(width/2, height - 2*inch, "Amin Constructions")
        
    # Subtitle (dark red color)
    c.setFont("Helvetica-Bold", 18)  # Bold font with larger size
    c.drawCentredString(width/2, height - 2.5*inch, "Fire Risk Assessment Report")
    
    # Try to find and add cover image
    cover_image_folder = os.path.join("uploads", form_id, "cover_image")
    cover_images = [f for f in os.listdir(cover_image_folder) if f.startswith(f"building_cover_image_{form_id}")]
    
    if cover_images:
        cover_image_path = os.path.join(cover_image_folder, cover_images[0])
        
        # Open image to get dimensions
        from PIL import Image
        img = Image.open(cover_image_path)
        img_width, img_height = img.size
        
        # Adjust image size (increased from 1/3 to 1/2 of A4 width for a larger image)
        img_display_size = width / 2
        aspect_ratio = img_height / img_width
        scaled_height = img_display_size * aspect_ratio
        
        # Center the image
        x_centered = (width - img_display_size) / 2
        y_positioned = height / 2 - scaled_height / 2
        
        # Draw the image
        c.drawImage(cover_image_path, x_centered, y_positioned, width=img_display_size, height=scaled_height)
    
    # Property Details Below Image (dark black color)
    c.setFillColorRGB(0, 0, 0)  # Dark black color
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height / 2 - scaled_height/2 - 50, f"Property: {property_name}")
    
    # Form ID
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height / 2 - scaled_height/2 - 80, f"Assessment ID: {form_id}")
    
    # Date
    current_date = datetime.now().strftime("%d %B %Y")
    c.drawCentredString(width/2, height / 2 - scaled_height/2 - 110, f"Date: {current_date}")
    
    # Footer (dark black color)
    c.setFillColorRGB(0, 0, 0)  # Dark black color
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, 50, "© 2024 Amin Constructions. All Rights Reserved.")
    
    # Save the PDF
    c.save()
    return pdf_path





def wrap_text(text, font, max_width):
    """
    Function to wrap text into multiple lines if it exceeds the max width.
    Uses getbbox() to get the width of the text.
    """
    lines = []
    words = text.split()
    current_line = ""
    
    for word in words:
        # Check if adding the word exceeds the max width
        test_line = current_line + " " + word if current_line else word
        bbox = font.getbbox(test_line)  # Get the bounding box of the text
        width = bbox[2] - bbox[0]  # The width is the difference between the right and left bounds

        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word  # Start a new line with the current word
    lines.append(current_line)  # Add the last line
    return lines


def generate_second_page_with_info(address, assessment_date, next_assessment_date, assessor, responsible_person, form_id):
    # Load the image
    image_path = "second_page_template.png"
    # Define the output path with dynamic form_id
    output_path = f"downloads/second_page/second_page_{form_id}.pdf"

    # Check if the directory exists, and create it if it doesn't
    directory = os.path.dirname(output_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    image = Image.open(image_path)

    # Create a drawing object
    draw = ImageDraw.Draw(image)

    # Specify the correct font path for Mac
    font_path_mac = "/Library/Fonts/Arial Unicode.ttf"  # Correct font for Mac

    # Try to detect if the system is Mac or Linux
    system = platform.system()

    if system == 'Darwin':  # For macOS
        font_path = font_path_mac
    elif system == 'Linux':  # For Linux
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Example for Linux
    else:
        font_path = "/path/to/your/font.ttf"  # Provide your custom font

    # Load the font with a larger size
    font = ImageFont.truetype(font_path, size=30)  # Adjust font size as needed

    # Define max width for the text (width before splitting)
    max_width = 500  # This is just an example, adjust based on your image's layout

    # Wrap address if it's too long
    address_lines = wrap_text(address, font, max_width)

    # List of texts and their corresponding positions
    texts = [
        (address_lines[0], (180, 540)),  # First line of address
        (address_lines[1] if len(address_lines) > 1 else '', (180, 580)),  # Second line of address, if it exists
        (assessment_date, (180, 670)),
        (next_assessment_date, (180, 780)),
        (assessor, (180, 900)),
        (responsible_person, (180, 1100)),
    ]

    # Set text color to black
    text_color = (0, 0, 0)  # Black color (R, G, B)

    # Add text to the image
    for text, position in texts:
        draw.text(position, text, fill=text_color, font=font)

    # Convert the image to RGB if it's not already in that mode
    image = image.convert("RGB")

    # Define A4 size at 300 DPI (A4 size is 595 x 842 pixels at 72 DPI, but at 300 DPI it's 2480 x 3508 pixels)
    a4_size_dpi_300 = (2480, 3508)  # A4 dimensions at 300 DPI

    # Resize the image to fit A4 size with high quality
    image = image.resize(a4_size_dpi_300, Image.Resampling.LANCZOS)  # Using LANCZOS for high-quality resampling

    # Save the image as a PDF with 300 DPI for high quality
    image.save(output_path, "PDF", resolution=300)

    print(f"Image saved at {output_path}")

    print(f"Image saved at {output_path}")

    return output_path



