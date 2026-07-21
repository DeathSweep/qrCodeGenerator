from flask import Flask, request, send_file, jsonify, render_template
from flask_cors import CORS
import qrcode
from PIL import Image, ImageDraw
import io
import base64
import logging
from urllib.parse import urlparse

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

CORS(app)
logging.basicConfig(level=logging.INFO)

LOGO_RATIO = 0.35
BOX_SIZE = 10
BORDER = 2
MAX_IMAGE_DIM = 2000
ALLOWED_FORMATS = {"PNG", "JPEG", "WEBP"}
SERVICE_NAME = "qr-generator"
SERVICE_VERSION = "1.0.0"


def api_error(message, status=400):
    return jsonify({"success": False, "message": message}), status


def validate_url(link: str) -> bool:
    if not link or not isinstance(link, str):
        return False
    
    link = link.strip()
    if not link.startswith(('http://', 'https://')):
        link = 'https://' + link
    
    p = urlparse(link)
    if p.scheme not in ("http", "https"):
        return False
    if not p.netloc:
        return False
    return True


def decode_logo(image_b64: str):
    # Safety check: if string is empty, null, or invalid, return None
    if not image_b64 or not isinstance(image_b64, str) or image_b64.strip() in ("", "null", "None"):
        return None

    if image_b64.startswith("data:image"):
        image_b64 = image_b64.split(",", 1)[1]
    
    try:
        # Avoid decoding empty strings
        decoded_bytes = base64.b64decode(image_b64)
        if not decoded_bytes:
            return None

        img = Image.open(io.BytesIO(decoded_bytes))
        if img.format not in ALLOWED_FORMATS:
            raise ValueError("Unsupported image format.")
        if img.width > MAX_IMAGE_DIM or img.height > MAX_IMAGE_DIM:
            raise ValueError("Image dimensions are too large.")
        return img.convert("RGBA")
    except Exception as e:
        raise ValueError(f"Invalid image format or corrupted upload: {str(e)}")


def create_qr(link: str, fill_color="#1667A6", back_color="white"):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=BOX_SIZE,
        border=BORDER,
    )
    qr.add_data(link)
    qr.make(fit=True)
    return qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")


def overlay_logo(qr_img, logo, bg_fill=False):
    w, h = qr_img.size
    size = int(min(w, h) * LOGO_RATIO)
    logo = logo.resize((size, size), Image.LANCZOS)

    x = (w - size) // 2
    y = (h - size) // 2

    if bg_fill:
        pad = int(size * 0.15)
        bg = Image.new("RGBA", (size + pad*2, size + pad*2), (255, 255, 255, 230))
        bg.paste(logo, (pad, pad), logo)
        logo_to_paste = bg
        paste_x = x - pad
        paste_y = y - pad
    else:
        logo_to_paste = logo
        paste_x = x
        paste_y = y

    out = qr_img.copy()
    out.paste(logo_to_paste, (paste_x, paste_y), logo_to_paste)
    return out


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate_qr", methods=["POST"])
def generate_qr():
    try:
        data = request.get_json(silent=True)
        if not data:
            return api_error("Invalid JSON payload.")
        
        link = str(data.get("link", "")).strip()
        image = data.get("image")  # Don't force str() conversion here so we handle None/null properly
        fill_color = str(data.get("fill_color", "#1667A6")).strip()
        bg_color = str(data.get("bg_color", "white")).strip()
        bg_fill = data.get("bg_fill", False)
        
        if not link:
            return api_error("Link is required.")
        
        if not link.startswith(('http://', 'https://')):
            link = 'https://' + link
        
        if not validate_url(link):
            return api_error("Please enter a valid domain or URL.")
        
        # Always create the base QR code first
        qr_img = create_qr(link, fill_color=fill_color, back_color=bg_color)
        
        # Only attempt to decode and overlay if an image string was passed
        logo = decode_logo(image) if image else None
        
        if logo:
            final = overlay_logo(qr_img, logo, bg_fill=bg_fill)
        else:
            final = qr_img
        
        output = io.BytesIO()
        final.save(output, format="PNG", optimize=True)
        output.seek(0)
        
        app.logger.info(f"QR generated successfully for: {link}")
        
        return send_file(
            output,
            mimetype="image/png",
            as_attachment=True,
            download_name="qr_code.png",
        )
    except ValueError as e:
        return api_error(str(e))
    except Exception:
        app.logger.exception("QR generation failed")
        return api_error("Internal server error", 500)

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)