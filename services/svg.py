import re

def clean_svg(svg):
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r">\s+<", "><", svg)
    return svg.strip()

def add_background(svg, bg_type, color1, color2):
    if bg_type == "transparent":
        return svg
    if bg_type == "solid":
        markup = f'<rect width="100%" height="100%" fill="{color1}" />'
    elif bg_type == "gradient":
        markup = (
            '<defs><linearGradient id="riGrad" x1="0%" y1="0%" x2="100%" y2="100%">'
            f'<stop offset="0%" stop-color="{color1}"/>'
            f'<stop offset="100%" stop-color="{color2}"/>'
            '</linearGradient></defs>'
            '<rect width="100%" height="100%" fill="url(#riGrad)"/>'
        )
    else:
        return svg
    m = re.search(r"<svg[^>]*>", svg, re.I)
    return svg.replace(m.group(0), m.group(0)+markup, 1) if m else svg

def svg_size(svg):
    m = re.search(r'<svg[^>]*viewBox="([^"]+)"', svg, re.I)
    return m.group(1) if m else ""
