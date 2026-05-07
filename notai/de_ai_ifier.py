import os
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import argparse

def add_film_grain(img, intensity=0.04):
    """Add random noise (film grain) to the image."""
    img_array = np.array(img)
    # Generate Gaussian noise
    noise = np.random.normal(0, intensity * 255, img_array.shape)
    # Add noise and clip values to valid range
    noisy_img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy_img_array)

def apply_vignette(img, intensity=0.3):
    """Apply a subtle vignette effect to the edges."""
    width, height = img.size
    # Create coordinate grid
    x, y = np.meshgrid(np.linspace(-1, 1, width), np.linspace(-1, 1, height))
    radius = np.sqrt(x**2 + y**2)
    
    # Calculate mask
    mask = 1 - np.clip(radius - 0.5, 0, 1) * intensity
    
    img_array = np.array(img)
    if len(img_array.shape) == 3:
        mask = np.expand_dims(mask, axis=-1)
    
    vignette_img_array = np.clip(img_array * mask, 0, 255).astype(np.uint8)
    return Image.fromarray(vignette_img_array)

def make_less_ai(input_path, output_path):
    """Process an image to make it look more like a real photograph."""
    try:
        print(f"Loading {input_path}...")
        img = Image.open(input_path).convert('RGB')
        
        # 1. Soften the image slightly to remove AI hyper-sharpness
        img = img.filter(ImageFilter.GaussianBlur(radius=0.4))
        
        # 2. Reduce contrast slightly (mimics flat film profiles)
        contrast_enhancer = ImageEnhance.Contrast(img)
        img = contrast_enhancer.enhance(0.9)
        
        # 3. Reduce saturation slightly (AI tends to over-saturate)
        color_enhancer = ImageEnhance.Color(img)
        img = color_enhancer.enhance(0.85)
        
        # 4. Add film grain
        img = add_film_grain(img, intensity=0.035)
        
        # 5. Add vignette
        img = apply_vignette(img, intensity=0.35)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Save the result
        img.save(output_path, quality=95)
        print(f"✅ Successfully processed and saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {input_path}: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process an AI image to make it look like a real photograph.")
    parser.add_argument("input", help="Path to the original AI generated image")
    parser.add_argument("output", help="Path to save the processed image")
    
    args = parser.parse_args()
    
    make_less_ai(args.input, args.output)
