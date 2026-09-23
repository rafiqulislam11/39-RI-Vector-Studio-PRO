import os
import tempfile
import vtracer

PRESETS = {
    "fast":   dict(color_precision=5, filter_speckle=8, length_threshold=7.0, corner_threshold=65),
    "balanced": dict(color_precision=7, filter_speckle=4, length_threshold=5.0, corner_threshold=60),
    "high":   dict(color_precision=8, filter_speckle=3, length_threshold=4.0, corner_threshold=55),
    "ultra":  dict(color_precision=8, filter_speckle=1, length_threshold=3.5, corner_threshold=45),
}

def vectorize(image, preset="balanced", color_precision=7, filter_speckle=4,
              detail=4, smoothness=4):
    p = PRESETS.get(preset, PRESETS["balanced"]).copy()

    p["color_precision"] = max(1, min(8, int(color_precision)))
    p["filter_speckle"] = max(0, min(128, int(filter_speckle)))

    # VTracer 0.6.x requires length_threshold >= 3.5.
    # The old build generated values such as 3.0 for the default Detail=4,
    # which caused the Magic Vector request to fail.
    detail = max(1, min(7, int(detail)))
    smoothness = max(1, min(7, int(smoothness)))

    p["length_threshold"] = max(3.5, min(10.0, 8.0 - detail * 0.5))
    p["corner_threshold"] = max(30, min(90, 75 - smoothness * 5))

    in_path = None
    out_path = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            in_path = f.name
            image.save(in_path, "PNG")

        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            out_path = f.name

        vtracer.convert_image_to_svg_py(
            in_path,
            out_path,
            colormode="color",
            hierarchical="stacked",
            mode="spline",
            filter_speckle=p["filter_speckle"],
            color_precision=p["color_precision"],
            layer_difference=16,
            corner_threshold=p["corner_threshold"],
            length_threshold=p["length_threshold"],
            max_iterations=10,
            splice_threshold=45,
            path_precision=3,
        )

        if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
            raise RuntimeError("VTracer SVG output তৈরি করতে পারেনি।")

        with open(out_path, "r", encoding="utf-8") as f:
            svg = f.read()

        if "<svg" not in svg.lower():
            raise RuntimeError("VTracer valid SVG output দেয়নি।")

        return svg

    except Exception as e:
        raise RuntimeError(f"VTracer error: {type(e).__name__}: {e}") from e

    finally:
        for pth in (in_path, out_path):
            if pth and os.path.exists(pth):
                try:
                    os.remove(pth)
                except OSError:
                    pass
