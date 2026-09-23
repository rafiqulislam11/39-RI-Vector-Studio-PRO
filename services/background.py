def remove_background(image):
    try:
        from rembg import remove
        return remove(image)
    except Exception as e:
        raise RuntimeError(f"rembg background removal failed: {e}")
