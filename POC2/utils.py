from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import reportlab
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from PIL import Image, ImageDraw, ImageFont
import os

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
