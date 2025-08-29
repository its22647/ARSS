from PIL import Image, ImageDraw, ImageFont

def generate_logo():
    """Creates and saves a simple text-based logo."""
    
    # Create a blank image (200x100) with a white background
    img = Image.new("RGB", (200, 100), color="white")
    draw = ImageDraw.Draw(img)

    # Define text for the logo
    text = "Anti-Ransomware"
    text_color = (0, 0, 0)  # Black color

    # Load a font (Arial) or use the default if missing
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    # Calculate text position using textbbox()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((200 - text_width) // 2, (100 - text_height) // 2)

    # Add text to the image
    draw.text(position, text, fill=text_color, font=font)

    # Save the logo as 'logo.png'
    img.save("logo.png")

    print("✅ Logo created successfully as 'logo.png'")

# Run the function when the script is executed
if __name__ == "__main__":
    generate_logo()
