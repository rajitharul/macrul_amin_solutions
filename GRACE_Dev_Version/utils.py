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

import os
from reportlab.lib.pagesizes import A4 
from reportlab.lib.units import inch 
from reportlab.pdfgen import canvas 
from PIL import Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER

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
    
    # Margins
    margin_x = 0.75 * inch  # Symmetric left and right margins
    margin_y = 0.5 * inch  # Top and bottom margins
    
    # Horizontal and vertical spacing
    horizontal_padding = 0.5 * inch  # Space between columns
    vertical_padding = 0.3 * inch  # Space between rows
    
    # Calculate image size to fit two columns with symmetric margins
    img_size = (width - 2 * margin_x - horizontal_padding) / 2
    
    # White background for the entire page
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Header for Reference Images
    header_text = "Reference Images"
    header_font_size = 20
    header_font = "Helvetica-Bold"
    
    # Calculate header dimensions
    text_width = c.stringWidth(header_text, header_font, header_font_size)
    text_height = header_font_size  # Approximate height of the text
    header_padding = 0.2 * inch  # Padding around the text
    
    # Dark red background for the header
    c.setFillColorRGB(0.9, 0, 0)  # Dark red color
    c.rect(
        (width - text_width) / 2 - header_padding,  # X position (centered)
        height - margin_y - text_height - header_padding,  # Y position
        text_width + 2 * header_padding,  # Width of the background
        text_height + 2 * header_padding,  # Height of the background
        fill=1,
        stroke=0
    )
    
    # White text for the header
    c.setFillColorRGB(1, 1, 1)  # White color
    c.setFont(header_font, header_font_size)
    c.drawCentredString(width / 2, height - margin_y - text_height, header_text)
    
    # Get list of image files
    image_files = [f for f in os.listdir(image_folder)
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    
    # Caption style
    caption_style = ParagraphStyle(
        'CaptionStyle',
        fontName='Helvetica',
        fontSize=10,
        textColor='black',
        alignment=TA_CENTER,
        leading=12  # Line height
    )
    
    # Track vertical position - minimal gap, start very close to the header
    y_position = height - margin_y - 0.2 * inch - (text_height + 2 * header_padding)
    
    # X positions for two columns with symmetric margins
    x_positions = [
        margin_x, 
        margin_x + img_size + horizontal_padding
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
        
        # Draw image
        c.drawImage(image_path, x_positions[current_column], y_position - scaled_height,
                    width=img_size, height=scaled_height, preserveAspectRatio=True)
        
        # Add image name below the image
        image_name = os.path.splitext(filename)[0]  # Remove file extension
        
        # Prepare paragraph for caption
        para = Paragraph(image_name, caption_style)
        
        # Calculate paragraph height
        para_width = img_size
        para_height = para.wrap(para_width, 100)[1]
        
        # Position caption below the image with some padding
        caption_y = y_position - scaled_height - 15 - para_height
        
        # Draw the paragraph
        para.drawOn(c, x_positions[current_column], caption_y)
        
        # Move to next column/row
        current_column += 1
        if current_column > 1:
            current_column = 0
            y_position -= scaled_height + vertical_padding + para_height + 30  # Move to next row
    
    # Save PDF
    c.save()



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
    
    # Dark Red Color for Heading
    dark_red_color = (0.9, 0, 0)  # Dark red RGB
    
    # Calculate maximum width for text (accounting for margins)
    header_margin = 50  # Margin from the sides
    max_text_width = width - 2 * header_margin - 20  # 20 pixels padding on each side
    
    # Create a temporary font object for measuring text
    temp_font = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", size=24)
    
    # Wrap the property name if it's too long
    wrapped_lines = wrap_text(property_name, temp_font, max_text_width)
    
    # Calculate line height and starting position
    line_height = 30  # Approximate height per line
    text_start_y = height - 1.8 * inch  # Starting position from top
    
    # Set font and color for the heading
    c.setFillColorRGB(*dark_red_color)  # Red color for text
    c.setFont("Helvetica-Bold", 24)  # Larger font size
    
    # Draw each line of text
    for i, line in enumerate(wrapped_lines):
        text_y_position = text_start_y - (i * line_height)
        c.drawCentredString(width / 2, text_y_position, line)
    
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
    c.drawCentredString(width / 2, height / 2 - scaled_height / 2 - 50, f"Property: {property_name}")
    
    # Form ID
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height / 2 - scaled_height / 2 - 80, f"Assessment ID: {form_id}")
    
    # Date
    current_date = datetime.now().strftime("%d %B %Y")
    c.drawCentredString(width / 2, height / 2 - scaled_height / 2 - 110, f"Date: {current_date}")
    
    # Footer (dark black color)
    c.setFillColorRGB(0, 0, 0)  # Dark black color
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, 50, "© Amin Contractors. All Rights Reserved.")
    
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
        font_path = "C:\\Windows\\Fonts\\arial.ttf"  # Provide your custom font

    # Load the font with a larger size
    font = ImageFont.truetype(font_path, size=30)  # Adjust font size as needed

    # Define max width for the text (width before splitting)
    max_width = 500  # This is just an example, adjust based on your image's layout

    # Wrap address if it's too long
    address_lines = wrap_text(address, font, max_width)

    # List of texts and their corresponding positions
    texts = [
        (address_lines[0], (180, 545)),  # First line of address
        (address_lines[1] if len(address_lines) > 1 else '', (180, 585)),  # Second line of address, if it exists
        (assessment_date, (180, 673)),
        (next_assessment_date, (180, 785)),
        (assessor, (180, 910)),
        (responsible_person, (180, 1120)),
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



