import io
import time
import os
import traceback

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError

from config import ALLOWED_TYPES, MAX_FILE_SIZE, MAX_DIMENSION
from services.background import remove_background
from services.preprocess import preprocess
from services.vectorizer import vectorize
from services.svg import clean_svg, add_background, svg_size

app = FastAPI(title="RI Vector Studio PRO v3.2 Fixed", version="3.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("logs", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
async def health():
    checks = {"vtracer": False, "rembg": False}
    errors = {}
    try:
        import vtracer
        checks["vtracer"] = True
        checks["vtracer_version"] = getattr(vtracer, "__version__", "installed")
    except Exception as e:
        errors["vtracer"] = str(e)

    try:
        import rembg
        checks["rembg"] = True
    except Exception as e:
        errors["rembg"] = str(e)

    return {
        "status": "ok" if checks["vtracer"] else "error",
        "version": "3.2.0",
        "checks": checks,
        "errors": errors,
    }

@app.post("/api/vectorize")
async def api_vectorize(
    file: UploadFile = File(...),
    remove_bg: bool = Form(True),
    enhance: bool = Form(False),
    denoise: bool = Form(False),
    preset: str = Form("balanced"),
    color_precision: int = Form(7),
    filter_speckle: int = Form(4),
    detail: int = Form(4),
    smoothness: int = Form(4),
    bg_type: str = Form("transparent"),
    bg_color1: str = Form("#ffffff"),
    bg_color2: str = Form("#4f46e5"),
):
    started = time.perf_counter()

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "PNG, JPG/JPEG অথবা WEBP ব্যবহার করুন।")

    data = await file.read()
    if not data:
        raise HTTPException(400, "Image file খালি।")

    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(413, "Image size সর্বোচ্চ 20MB হতে পারবে।")

    try:
        image = Image.open(io.BytesIO(data)).convert("RGBA")
        image.load()
    except UnidentifiedImageError:
        raise HTTPException(400, "Image fileটি valid নয়।")
    except Exception as e:
        raise HTTPException(400, f"Image read করা যায়নি: {e}")

    if image.width > MAX_DIMENSION or image.height > MAX_DIMENSION:
        raise HTTPException(400, "Image dimension সর্বোচ্চ 5000×5000 হতে পারবে।")

    try:
        image = preprocess(image, enhance, denoise)

        warning = None
        if remove_bg:
            try:
                image = remove_background(image)
            except Exception as e:
                warning = f"AI Background Removal skipped: {e}"

        svg = vectorize(
            image, preset, color_precision, filter_speckle,
            detail, smoothness
        )
        svg = add_background(svg, bg_type, bg_color1, bg_color2)
        svg = clean_svg(svg)

        if not svg or "<svg" not in svg.lower():
            raise RuntimeError("SVG output empty/invalid।")

        return JSONResponse({
            "success": True,
            "svg": svg,
            "width": image.width,
            "height": image.height,
            "viewBox": svg_size(svg),
            "processing_time": round(time.perf_counter() - started, 2),
            "warning": warning,
        })

    except HTTPException:
        raise
    except Exception as e:
        with open("logs/error.log", "a", encoding="utf-8") as log:
            log.write(
                f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
                f"{type(e).__name__}: {e}\n"
            )
            log.write(traceback.format_exc())
        raise HTTPException(
            500,
            f"Magic Vector failed: {type(e).__name__}: {e}"
        )
