import streamlit as st
from PIL import Image
import numpy as np
import cv2
from io import BytesIO
import requests
from streamlit_lottie import st_lottie

st.set_page_config(
    page_title="Just Post It - Social Media Converter", 
    layout="wide",
    menu_items={
        'About': "Made with Love by Sughosh"
    }
)

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

st.title("🚀 Just Post It: Social Media Converter")
st.markdown("Convert your posts to 4K, change aspect ratios, and create carousels.")

import utils

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    
    st.markdown("### 🛠️ Enhancement Mode")
    content_type = st.radio(
        "What kind of content is this?",
        ["Text / Screenshot / Poster", "Natural Photo / Person"],
        help="Choose 'Text' for crisp edges. Choose 'Photo' for better color/contrast and natural details."
    )
    
    target_ratio = st.selectbox(
        "Target Platform / Format",
        [
            "Original",
            "Instagram Square (1:1)",
            "Instagram Portrait (4:5)",
            "Instagram Story / Reel (9:16)",
            "LinkedIn / Facebook Post (4:5)",
            "Twitter / X Landscape (16:9)",
            "YouTube Thumbnail (16:9)"
        ]
    )
    
    upscale_factor = st.slider("Upscale Factor", 1, 8, 2, help="2x = 4K-ish, 4x-8x = Ultra High Res (8K)")
    output_format = st.radio("Output Format", ["Single Image", "Carousel (Split Long Image)"])
    
    st.markdown("---")
    st.subheader("Branding")
    
    logo_source = st.radio("Logo Source", ["Upload Existing Logo", "Create from Image (Remove BG)"])
    
    logo_img = None
    if logo_source == "Upload Existing Logo":
        logo_file = st.file_uploader("Upload Logo", type=['png', 'jpg'])
        if logo_file:
            logo_img = Image.open(logo_file)
    else:
        logo_raw = st.file_uploader("Upload Image to Convert to Logo", type=['png', 'jpg', 'jpeg'])
        if logo_raw:
            st.info("Generating logo... (Removing background)")
            raw_img = Image.open(logo_raw)
            # Process immediately
            logo_img = utils.remove_background(raw_img)
            st.image(logo_img, caption="Generated Logo Preview", width=150)
            
    st.markdown("---")
    st.subheader("Style Options")
    card_mode = st.checkbox("Enable Card Mode (Rounded Corners & Shadow)", value=False)
    bg_type = st.radio(
        "Background Style", 
        ["Blurred Image", "Solid Color", "Adaptive Gradient", "Adaptive Solid"]
    )
    
    bg_color = "#000000" # Default
    if bg_type == "Solid Color":
        bg_color = st.color_picker("Choose Background Color", "#1E1E1E")

# File Upload
uploaded_file = st.file_uploader("Upload your post (Image)", type=['png', 'jpg', 'jpeg'])

if uploaded_file is None:
    # Lottie Animation when idle
    lottie_url = "https://assets5.lottiefiles.com/packages/lf20_wys2hpms.json" # Social media marketing animation
    lottie_json = load_lottieurl(lottie_url)
    if lottie_json:
        st_lottie(lottie_json, height=300)
    
    st.info("👆 Upload an image to get started!")

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Original Image")
        st.image(image, caption="Original Upload", use_container_width=True)
    
    with col2:
        st.subheader("Preview")
        if st.button("Process Image", type="primary", use_container_width=True):
            with st.spinner("Processing..."):
                # 1. Upscale
                if upscale_factor > 1:
                    processed_img = utils.upscale_image(image, factor=upscale_factor, content_type=content_type)
                else:
                    processed_img = image
                
                # 2. Format
                if output_format == "Carousel (Split Long Image)":
                    slides = utils.create_carousel_slides(
                        processed_img, 
                        target_ratio, 
                        logo=logo_img,
                        bg_type=bg_type,
                        custom_color=bg_color,
                        card_mode=card_mode
                    )
                    st.success(f"Generated {len(slides)} slides!")
                    
                    # Display slides in a grid or scroller
                    for idx, slide in enumerate(slides):
                        st.image(slide, caption=f"Slide {idx+1}", use_container_width=True)
                        
                        # Download button for each
                        buf = BytesIO()
                        slide.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        st.download_button(
                            label=f"Download Slide {idx+1}",
                            data=byte_im,
                            file_name=f"slide_{idx+1}.png",
                            mime="image/png",
                            key=f"btn_{idx}"
                        )
                        
                else:
                    # Single Image Mode
                    final_img = utils.resize_with_padding(
                        processed_img, 
                        target_ratio, 
                        logo=logo_img,
                        bg_type=bg_type,
                        custom_color=bg_color,
                        card_mode=card_mode
                    )
                    st.success("Processing Complete!")
                    st.image(final_img, caption="Final Image", use_container_width=True)
                    
                    buf = BytesIO()
                    final_img.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    st.download_button(
                        label="Download Image",
                        data=byte_im,
                        file_name="processed_post.png",
                        mime="image/png",
                        type="primary",
                        use_container_width=True
                    )

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: grey;">
        Made with ❤️ by Sughosh
    </div>
    """,
    unsafe_allow_html=True
)

