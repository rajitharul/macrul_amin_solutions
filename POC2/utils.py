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

    # Add title "Reference Pictures" at the top of the first page
    title_font_size = int(0.5 * dpi)  # Font size for the title
    title_margin = int(0.3 * dpi)  # Margin below the title
    title_canvas = Image.new("RGB", (page_width, title_font_size + title_margin), "white")
    draw = ImageDraw.Draw(title_canvas)
    title_font = ImageFont.truetype("arial.ttf", size=title_font_size)  # Use a TrueType font
    title_text = "Reference Pictures"
    text_bbox = draw.textbbox((0, 0), title_text, font=title_font)  # Calculate text bounding box
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (page_width - text_width) // 2
    text_y = (title_font_size - text_height) // 2
    draw.text((text_x, text_y), title_text, fill="black", font=title_font)
    page.paste(title_canvas, (0, 0))

    coords = [
        (0, title_font_size + title_margin),
        (page_width // 2, title_font_size + title_margin),
        (0, page_height // 2 + title_font_size + title_margin),
        (page_width // 2, page_height // 2 + title_font_size + title_margin),
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
