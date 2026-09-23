from PIL import Image, ImageEnhance, ImageFilter

def preprocess(image, enhance=False, denoise=False):
    image = image.convert("RGBA")
    if denoise:
        image = image.filter(ImageFilter.MedianFilter(size=3))
    if enhance:
        rgb = image.convert("RGB")
        rgb = ImageEnhance.Contrast(rgb).enhance(1.08)
        rgb = ImageEnhance.Sharpness(rgb).enhance(1.12)
        image = rgb.convert("RGBA")
    return image
