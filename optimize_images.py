from PIL import Image
from pathlib import Path

def is_likely_screenshot(img: Image) -> bool:
    """Determine if image is likely a screenshot/graphic rather than photo"""
    # Check for transparency
    if 'A' in img.getbands():
        return True
    
    # Try to get color count with higher limit
    try:
        colors = img.convert('RGB').getcolors(maxcolors=50000)
        # If we can get a color count and it's low, likely a graphic
        if colors is not None and len(colors) < 256:
            return True
    except Exception:
        pass
    
    return False

def optimize_images(
    input_dir: str = "input/images", 
    output_dir: str = "input/images_optimized", 
    max_width: int = 900
):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for img_path in input_path.glob('*'):
        if img_path.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.gif'}:
            continue
            
        print(f"Processing: {img_path.name}")
        try:
            img = Image.open(img_path)
            
            # Skip if image is smaller than max_width
            if img.size[0] <= max_width:
                print(f"Skipping {img_path.name} - already small enough")
                continue
                
            # Calculate new height maintaining aspect ratio
            ratio = max_width / img.size[0]
            new_size = (max_width, int(img.size[1] * ratio))
            
            # Resize using LANCZOS
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Determine if PNG should be kept
            keep_png = img_path.suffix.lower() == '.png' and is_likely_screenshot(img)
            
            output_name = img_path.stem + ('.png' if keep_png else '.jpg')
            output_file = output_path / output_name
            
            if not keep_png:
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.save(output_file, 'JPEG', quality=85, optimize=True)
            else:
                img.save(output_file, 'PNG', optimize=True)
            
            orig_size = img_path.stat().st_size / 1024  # KB
            new_size = output_file.stat().st_size / 1024  # KB
            print(f"Reduced from {orig_size:.1f}KB to {new_size:.1f}KB")
            
        except Exception as e:
            print(f"Error processing {img_path.name}: {str(e)}")
            continue

if __name__ == "__main__":
    optimize_images()