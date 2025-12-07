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

# --- Open Graph Tags (Workaround for Streamlit Cloud) ---
# Note: Streamlit Cloud usually handles this via settings, but we can try to inject it.
st.markdown("""
<head>
    <meta property="og:title" content="Just Post It 🚀" />
    <meta property="og:description" content="Convert your posts to 4K, change aspect ratios, and create viral carousels in seconds." />
    <meta property="og:image" content="https://raw.githubusercontent.com/SughoshDixit/just-post-it/main/Posts/30-day.jpg" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
</head>
""", unsafe_allow_html=True)

# --- Custom CSS for UI Improvements ---
st.markdown("""
<style>
    /* Gradient Title */
    h1 {
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF914D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    /* Card-like container for file uploader */
    .stFileUploader {
        padding: 2rem;
        border: 2px dashed #FF4B4B;
        border-radius: 10px;
        background-color: #f9f9f920;
    }
    
    /* Button Styling */
    div.stButton > button {
        background: linear-gradient(45deg, #FF4B4B, #FF914D);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        transition: transform 0.2s;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
    }
    
    /* Success Message */
    .stSuccess {
        border-radius: 10px;
        border-left: 5px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

st.title("🚀 Just Post It")
st.markdown("### The Ultimate Social Media Repurposing Tool")
st.markdown("transform your raw screenshots and photos into **viral-ready visuals** in seconds.")

import utils

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Configuration")
    
    with st.expander("🖼️ Content & Quality", expanded=True):
        st.markdown("#### Enhancement Mode")
        content_type = st.radio(
            "Content Type",
            ["Text / Screenshot / Poster", "Natural Photo / Person"],
            help="Choose 'Text' for crisp edges. Choose 'Photo' for better color/contrast and natural details.",
            label_visibility="collapsed"
        )
        
        upscale_factor = st.slider("Upscale Factor (x)", 1, 8, 2, help="2x = 4K-ish, 4x-8x = Ultra High Res (8K)")

    with st.expander("📱 Format & Platform", expanded=True):
        target_ratio = st.selectbox(
            "Target Platform",
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
        output_format = st.radio("Output Mode", ["Single Image", "Carousel (Split Long Image)"])
    
    with st.expander("🎨 Branding & Style", expanded=False):
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
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown("### How it works")
        st.markdown("""
        1. **Upload** your screenshot or photo.
        2. **Configure** the style (Square, Portrait, Carousel).
        3. **Process & Download** your viral-ready post!
        
        ✨ **Features:**
        - Auto-remove backgrounds for Logos
        - Smart 4K Upscaling
        - Automatic seamless Carousels
        """)
    with col_b:
        # Lottie Animation when idle
        lottie_url = "https://assets5.lottiefiles.com/packages/lf20_wys2hpms.json" # Social media marketing animation
        lottie_json = load_lottieurl(lottie_url)
        if lottie_json:
            st_lottie(lottie_json, height=250)
    
    st.info("👆 Upload an image in the sidebar or above to get started!")

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    st.markdown("---")
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("Original Image")
        st.image(image, caption=f"Original ({image.width}x{image.height})", use_container_width=True)
    
    with col2:
        st.subheader("Preview & Download")
        
        # Show original dimensions
        st.caption(f"📐 Original: {image.width} × {image.height} pixels")
        if upscale_factor > 1:
            expected_w = image.width * upscale_factor
            expected_h = image.height * upscale_factor
            st.caption(f"🎯 After {upscale_factor}x upscale: ~{expected_w} × {expected_h} pixels")
        
        if st.button("✨ Process Image", type="primary", use_container_width=True):
            with st.spinner("🎨 Magic in progress... Upscaling & Styling..."):
                # 1. Upscale
                if upscale_factor > 1:
                    processed_img = utils.upscale_image(image, factor=upscale_factor, content_type=content_type)
                    st.info(f"✅ Upscaled to {processed_img.width} × {processed_img.height} pixels")
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
                    # If Original format with no styling, use upscaled image directly
                    needs_formatting = (target_ratio != "Original" or logo_img or bg_type != "Blur" or card_mode)
                    
                    if not needs_formatting and upscale_factor > 1:
                        # Just return the upscaled image directly, no formatting needed
                        final_img = processed_img
                    else:
                        final_img = utils.resize_with_padding(
                            processed_img, 
                            target_ratio, 
                            logo=logo_img,
                            bg_type=bg_type,
                            custom_color=bg_color,
                            card_mode=card_mode
                        )
                    
                    st.success("Processing Complete!")
                    
                    # Show comparison if upscaled
                    if upscale_factor > 1:
                        st.markdown("#### 📊 Upscaling Quality Comparison")
                        comp_col1, comp_col2 = st.columns(2)
                        with comp_col1:
                            st.caption(f"Original: {image.width}×{image.height}px")
                            st.image(image, use_container_width=True)
                        with comp_col2:
                            st.caption(f"Upscaled ({upscale_factor}x): {processed_img.width}×{processed_img.height}px")
                            st.image(processed_img, use_container_width=True)
                        st.markdown("---")
                    
                    st.markdown("#### 🎨 Final Processed Image")
                    st.image(final_img, caption=f"Final Image ({final_img.width}×{final_img.height}px)", use_container_width=True)
                    
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

