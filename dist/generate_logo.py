from PIL import Image, ImageDraw, ImageFont

# Create a blank image (200x100) with a white background
img = Image.new("RGB", (200, 100), color="white")

# Draw on the image
draw = ImageDraw.Draw(img)

# Define text for logo
text = "Anti-Ransomware"
text_color = (0, 0, 0)  # Black color

# Load a font (optional, requires a .ttf font file in the same directory)
try:
    font = ImageFont.truetype("arial.ttf", 20)
except:
    font = None  # Use default font if arial.ttf is missing

# Calculate text position
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
position = ((200 - text_width) // 2, (100 - text_height) // 2)

# Add text to image
draw.text(position, text, fill=text_color, font=font)

# Save the logo as 'logo.png'
img.save("logo.png")

print("Logo created successfully as 'logo.png'")