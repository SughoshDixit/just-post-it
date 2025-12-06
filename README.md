# Just Post It 🚀

A social media repurposing tool that converts screenshots and posts into high-quality, organizational-style carousels.

## Features
- **4K Upscaling:** High-quality image resizing with sharpening.
- **Smart Aspect Ratio:** Converts images to 1:1, 4:5, or 16:9 without cropping text (uses blurred background padding).
- **Carousel Generator:** Automatically splits long screenshots (e.g., Twitter threads) into seamless carousel slides.
- **Branding:** Overlay your organization's logo on every slide.

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```

## Tech Stack
- **Python**
- **Streamlit** (UI)
- **Pillow (PIL)** & **OpenCV** (Image Processing)

