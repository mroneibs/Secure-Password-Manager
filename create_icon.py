from PIL import Image, ImageDraw

# Create a new image with a transparent background
size = (256, 256)
image = Image.new('RGBA', size, (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Draw a lock shape
padding = 40
width = size[0] - 2 * padding
height = size[1] - 2 * padding

# Lock body (rounded rectangle)
body_top = padding + height // 3
body_height = height - height // 3
draw.rounded_rectangle(
    [padding, body_top, padding + width, padding + height],
    radius=20,
    fill='black'
)

# Lock shackle (arc)
shackle_width = width // 2
shackle_left = padding + (width - shackle_width) // 2
shackle_right = shackle_left + shackle_width
shackle_top = padding
shackle_bottom = body_top

# Draw the shackle
draw.rounded_rectangle(
    [shackle_left, shackle_top, shackle_right, shackle_bottom],
    radius=10,
    fill='black'
)

# Save in different sizes
sizes = [16, 32, 48, 64, 128, 256]
images = []

for s in sizes:
    resized_image = image.resize((s, s), Image.Resampling.LANCZOS)
    images.append(resized_image)

# Save as ICO file
images[0].save(
    'icon.ico',
    format='ICO',
    sizes=[(s, s) for s in sizes],
    append_images=images[1:]
) 