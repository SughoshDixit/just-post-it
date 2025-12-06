import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageOps
from rembg import remove

# Aspect Ratio Dictionary
ASPECT_RATIOS = {
    "Instagram Square (1:1)": 1.0,
    "Instagram Portrait (4:5)": 4/5,
    "Instagram Story / Reel (9:16)": 9/16,
    "LinkedIn / Facebook Post (4:5)": 4/5,
    "Twitter / X Landscape (16:9)": 16/9,
    "YouTube Thumbnail (16:9)": 16/9
}

def remove_background(image: Image.Image) -> Image.Image:
    """
    Removes the background from an image using rembg (U2-Net).
    Returns a PNG image with transparency.
    """
    return remove(image)

def get_dominant_colors(image: Image.Image, num_colors=2):
    """
    Extracts dominant colors from the image using simple quantization.
    Returns a list of (R, G, B) tuples.
    """
    # Resize to speed up processing
    small_img = image.resize((150, 150))
    # Convert to RGB in case it's RGBA (transparency affects quantization)
    if small_img.mode == 'RGBA':
        small_img = small_img.convert('RGB')
        
    result = small_img.quantize(colors=num_colors)
    palette = result.getpalette()
    colors = [tuple(palette[i*3:i*3+3]) for i in range(num_colors)]
    return colors

def create_gradient(width, height, color1, color2):
    """Generates a vertical linear gradient image."""
    base = Image.new('RGB', (width, height), color1)
    top = Image.new('RGB', (width, height), color2)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def upscale_image(image: Image.Image, factor: int = 2, content_type: str = "Text/Post") -> Image.Image:
    """
    Upscale the image using different strategies based on content type.
    """
    if factor <= 1:
        return image
    
    width, height = image.size
    new_width = width * factor
    new_height = height * factor
    
    # High-quality resampling (Standard for both)
    upscaled = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    if content_type == "Text/Post":
        # For text, we want crisp edges.
        enhancer = ImageEnhance.Sharpness(upscaled)
        sharpness = 1.5 if factor < 4 else 1.2 
        upscaled = enhancer.enhance(sharpness)
    else: 
        # "Natural Photo / Person"
        # 1. Subtle Sharpening
        enhancer = ImageEnhance.Sharpness(upscaled)
        upscaled = enhancer.enhance(1.1) # Very mild sharpening
        
        # 2. Contrast Enhancement (Pop)
        enhancer = ImageEnhance.Contrast(upscaled)
        upscaled = enhancer.enhance(1.05)
        
        # 3. Color/Saturation Boost (Vibrance)
        enhancer = ImageEnhance.Color(upscaled)
        upscaled = enhancer.enhance(1.1)

    return upscaled

def add_rounded_corners(image: Image.Image, radius: int = 30) -> Image.Image:
    """Adds rounded corners to an image"""
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)
    
    output = image.copy()
    output.putalpha(mask)
    return output

def get_background(image: Image.Image, width: int, height: int, bg_type: str, custom_color: str) -> Image.Image:
    """Helper to generate background based on type."""
    if bg_type == "Solid Color":
        return Image.new("RGB", (width, height), custom_color)
    elif bg_type == "Adaptive Gradient":
        colors = get_dominant_colors(image, num_colors=2)
        return create_gradient(width, height, colors[0], colors[1])
    elif bg_type == "Adaptive Solid":
        colors = get_dominant_colors(image, num_colors=1)
        return Image.new("RGB", (width, height), colors[0])
    else: # Blur
        # Resize original to cover the canvas
        bg_scale = max(width / image.width, height / image.height)
        bg_w = int(image.width * bg_scale)
        bg_h = int(image.height * bg_scale)
        bg_img = image.resize((bg_w, bg_h), Image.Resampling.LANCZOS)
        # Crop center
        c_x = (bg_w - width) // 2
        c_y = (bg_h - height) // 2
        bg_img = bg_img.crop((c_x, c_y, c_x + width, c_y + height))
        return bg_img.filter(ImageFilter.GaussianBlur(radius=50))

def generate_even_shadow(width, height, radius, blur_radius):
    """
    Generates a shadow layer that is larger than the content to allow for even blurring on all sides.
    """
    expansion = int(blur_radius * 2.5) 
    shadow_w = width + expansion * 2
    shadow_h = height + expansion * 2
    
    shadow = Image.new("RGBA", (shadow_w, shadow_h), (0,0,0,0))
    shadow_draw = ImageDraw.Draw(shadow)
    
    # Draw rect centered in shadow canvas
    shadow_draw.rounded_rectangle(
        [(expansion, expansion), 
         (shadow_w - expansion, shadow_h - expansion)], 
        radius=radius, 
        fill=(0,0,0, 90) 
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    return shadow, expansion

def resize_with_padding(image: Image.Image, target_ratio_name: str, logo: Image.Image = None, 
                       bg_type: str = "Blur", custom_color: str = "#000000", card_mode: bool = False) -> Image.Image:
    """
    Resizes image to fit target aspect ratio.
    """
    ratio = ASPECT_RATIOS.get(target_ratio_name, 1.0)
        
    img_w, img_h = image.size
    
    # Base Target Width (High Res)
    target_w = max(img_w, 2160) 
    
    if ratio < 1: # Vertical
        target_h = int(target_w / ratio)
    else: # Horizontal
        target_h = int(target_w / ratio)
        
    # Create background
    bg = get_background(image, target_w, target_h, bg_type, custom_color)

    # Prepare Foreground
    scale_factor = 0.80 if card_mode else 1.0 
    
    scale_w = target_w / img_w
    scale_h = target_h / img_h
    scale = min(scale_w, scale_h) * scale_factor
    
    new_fg_w = int(img_w * scale)
    new_fg_h = int(img_h * scale)
    fg = image.resize((new_fg_w, new_fg_h), Image.Resampling.LANCZOS)
    
    if card_mode:
        radius = int(min(target_w, target_h) * 0.03) 
        fg = add_rounded_corners(fg, radius=radius)
        
        # Generate Even 4-sided Shadow
        blur_radius = int(min(target_w, target_h) * 0.02)
        shadow, expansion = generate_even_shadow(new_fg_w, new_fg_h, radius, blur_radius)
        
        # Calculate positions
        x_offset = (target_w - new_fg_w) // 2
        y_offset = (target_h - new_fg_h) // 2
        
        # Paste shadow centered behind FG
        bg.paste(shadow, (x_offset - expansion, y_offset - expansion), shadow)
        bg.paste(fg, (x_offset, y_offset), fg)
    else:
        x_offset = (target_w - new_fg_w) // 2
        y_offset = (target_h - new_fg_h) // 2
        bg.paste(fg, (x_offset, y_offset))
    
    # Overlay Logo
    if logo:
        logo_w = int(target_w * 0.15)
        logo_aspect = logo.width / logo.height
        logo_h = int(logo_w / logo_aspect)
        logo_resized = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        
        padding = int(target_w * 0.05)
        bg.paste(logo_resized, (target_w - logo_w - padding, padding), logo_resized if logo_resized.mode == 'RGBA' else None)
    
    return bg

def create_carousel_slides(image: Image.Image, target_ratio_name: str, logo: Image.Image = None,
                          bg_type: str = "Blur", custom_color: str = "#000000", card_mode: bool = False):
    """
    Splits a long image into multiple carousel slides seamlessly.
    """
    ratio = ASPECT_RATIOS.get(target_ratio_name, 1.0)
    
    img_w, img_h = image.size
    
    # 1. Determine Dimensions
    slide_width = max(img_w, 2160)
    slide_height = int(slide_width / ratio)
    
    # 2. Calculate Content Scaling
    padding_factor = 0.80 if card_mode else 1.0
    content_target_width = int(slide_width * padding_factor)
    
    scale_ratio = content_target_width / img_w
    content_new_height = int(img_h * scale_ratio)
    
    # 3. Determine Number of Slides needed
    vertical_padding = int((slide_height - (slide_height * padding_factor)) / 2) if card_mode else 0
    
    total_content_height_with_padding = content_new_height + (vertical_padding * 2)
    num_slides = int(np.ceil(total_content_height_with_padding / slide_height))
    
    # 4. Create the "Giant Canvas"
    total_canvas_height = num_slides * slide_height
    
    # Use helper for background
    canvas = get_background(image, slide_width, total_canvas_height, bg_type, custom_color)

    # 5. Process the Foreground (The Long Image)
    fg = image.resize((content_target_width, content_new_height), Image.Resampling.LANCZOS)
    
    if card_mode:
        radius = int(slide_width * 0.03)
        fg = add_rounded_corners(fg, radius=radius)
        
        # Generate Even 4-sided Shadow
        blur_radius = int(slide_width * 0.02)
        shadow, expansion = generate_even_shadow(content_target_width, content_new_height, radius, blur_radius)
        
        # Center the CARD in the CANVAS
        x_pos = (slide_width - content_target_width) // 2
        y_pos = (total_canvas_height - content_new_height) // 2
        
        # Paste Shadow then FG
        canvas.paste(shadow, (x_pos - expansion, y_pos - expansion), shadow)
        canvas.paste(fg, (x_pos, y_pos), fg)
        
    else:
        x_pos = (slide_width - content_target_width) // 2
        y_pos = (total_canvas_height - content_new_height) // 2
        canvas.paste(fg, (x_pos, y_pos))

    # 6. Slice the Giant Canvas
    slides = []
    for i in range(num_slides):
        top = i * slide_height
        bottom = (i + 1) * slide_height
        slide = canvas.crop((0, top, slide_width, bottom))
        
        # Add logo to each slide
        if logo:
            logo_w = int(slide_width * 0.15)
            logo_aspect = logo.width / logo.height
            logo_h = int(logo_w / logo_aspect)
            logo_resized = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
            padding = int(slide_width * 0.05)
            slide.paste(logo_resized, (slide_width - logo_w - padding, padding), logo_resized if logo_resized.mode == 'RGBA' else None)
            
        slides.append(slide)
            
    return slides
