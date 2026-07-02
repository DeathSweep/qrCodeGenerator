
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

# Change to your frontend URL in production
CORS(app)

logging.basicConfig(level=logging.INFO)

LOGO_RATIO = 0.25
BOX_SIZE = 10
BORDER = 4
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
    
    # If no scheme is provided, assume https
    if not link.startswith(('http://', 'https://')):
        link = 'https://' + link
    
    p = urlparse(link)
    
    # Allow http, https, and also www. domains
    if p.scheme not in ("http", "https"):
        return False
    
    # Must have a network location (domain)
    if not p.netloc:
        return False
    
    return True


def decode_logo(image_b64: str):
    if image_b64.startswith("data:image"):
        image_b64 = image_b64.split(",", 1)[1]
    try:
        img = Image.open(io.BytesIO(base64.b64decode(image_b64)))
        if img.format not in ALLOWED_FORMATS:
            raise ValueError("Unsupported image format.")
        if img.width > MAX_IMAGE_DIM or img.height > MAX_IMAGE_DIM:
            raise ValueError("Image dimensions are too large.")
        return img.convert("RGBA")
    except Exception as e:
        raise ValueError(str(e))


def create_qr(link: str):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=BOX_SIZE,
        border=BORDER,
    )
    qr.add_data(link)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGBA")


def overlay_logo(qr_img, logo):
    w, h = qr_img.size
    size = int(min(w, h) * LOGO_RATIO)
    logo = logo.resize((size, size), Image.LANCZOS)

    x = (w - size) // 2
    y = (h - size) // 2

    pad = int(size * 0.12)
    bg = Image.new("RGBA", qr_img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle(
        [x - pad, y - pad, x + size + pad, y + size + pad],
        radius=pad,
        fill="white",
    )

    out = Image.alpha_composite(qr_img, bg)
    out.paste(logo, (x, y), logo)
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
        image = str(data.get("image", "")).strip()
        
        if not link:
            return api_error("Link is required.")
        
        # Normalize URL before validation
        if not link.startswith(('http://', 'https://')):
            link = 'https://' + link
        
        if not validate_url(link):
            return api_error("Please enter a valid domain or URL.")
        
        if not image:
            return api_error("Image is required.")
        
        logo = decode_logo(image)
        final = overlay_logo(create_qr(link), logo)
        
        output = io.BytesIO()
        final.save(output, format="PNG", optimize=True)
        output.seek(0)
        
        app.logger.info(f"QR generated successfully for: {link}")
        
        return send_file(
            output,
            mimetype="image/png",
            as_attachment=True,
            download_name="qr_with_logo.png",
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
