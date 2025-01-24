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
    """
    Combine all images in a folder into a single PDF with 4 images per page,
    maintaining their original resolution, and adding thick white borders.

    :param form_id: Unique identifier for the form to locate the folder and name the PDF.
    """
    output_pdf_path = f"downloads/reference_pictures_{form_id}.pdf"
    image_folder = f"uploads/{form_id}"  # Path to the folder containing images

    # Get a list of all image files in the folder
    image_files = [
        os.path.join(image_folder, file)
        for file in sorted(os.listdir(image_folder))
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
    ]

    if not image_files:
        print("No images found in the folder.")
        return

    # Define high-resolution page size (e.g., 300 DPI A4 size)
    dpi = 300
    page_width, page_height = int(8.27 * dpi), int(11.69 * dpi)  # A4 size in pixels at 300 DPI
    max_width, max_height = page_width // 2, page_height // 2  # Maximum size for each image including borders
    border_thickness = int(0.1 * dpi)  # Thickness of the white border in pixels

    pages = []
    page = Image.new("RGB", (page_width, page_height), "white")

    # Adjust title font size to make it smaller
    title_font_size = int(0.3 * dpi)  # Reduced font size
    title_margin = int(0.3 * dpi)  # Margin below the title
    title_canvas_height = title_font_size + title_margin
    title_canvas = Image.new("RGB", (page_width, title_canvas_height), "white")
    draw = ImageDraw.Draw(title_canvas)

    # Use a professional font
    try:
        title_font = ImageFont.truetype("arial.ttf", size=title_font_size)  # Adjust font path if needed
    except IOError:
        title_font = ImageFont.load_default()  # Fallback to default font if Arial is not found
    
    title_text = "Reference Picture Section"
    text_bbox = draw.textbbox((0, 0), title_text, font=title_font)  # Calculate text bounding box
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (page_width - text_width) // 2
    text_y = (title_font_size - text_height) // 2
    draw.text((text_x, text_y), title_text, fill="black", font=title_font)
    page.paste(title_canvas, (0, 0))

    coords = [
        (0, title_canvas_height),
        (page_width // 2, title_canvas_height),
        (0, page_height // 2 + title_canvas_height),
        (page_width // 2, page_height // 2 + title_canvas_height),
    ]
    current_image_index = 0

    for image_file in image_files:
        img = Image.open(image_file).convert("RGB")

        # Maintain aspect ratio while scaling dimensions to fit within the max size
        img_ratio = img.width / img.height
        if img.width > img.height:
            scale = min((max_width - 2 * border_thickness) / img.width, (max_height - 2 * border_thickness) / img.height)
        else:
            scale = min((max_width - 2 * border_thickness) / img.width, (max_height - 2 * border_thickness) / img.height)

        new_width = int(img.width * scale)
        new_height = int(img.height * scale)

        # Create a blank canvas larger than the image to include borders
        img_canvas = Image.new("RGB", (max_width, max_height), "white")
        x_offset = (max_width - new_width) // 2
        y_offset = (max_height - new_height) // 2
        img_canvas.paste(img.resize((new_width, new_height), Image.Resampling.LANCZOS), (x_offset, y_offset))

        # Paste the canvas onto the page
        x, y = coords[current_image_index % 4]
        page.paste(img_canvas, (x, y))
        current_image_index += 1

        # Save page when 4 images are added or last image is processed
        if current_image_index % 4 == 0 or current_image_index == len(image_files):
            pages.append(page)
            if current_image_index != len(image_files):
                page = Image.new("RGB", (page_width, page_height), "white")

    # Save all pages into a single PDF
    if pages:
        pages[0].save(output_pdf_path, save_all=True, append_images=pages[1:], resolution=dpi)
        print(f"PDF created successfully at {output_pdf_path}")


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
