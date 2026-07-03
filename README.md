# QR Generator with Logo

A simple and fast **Flask-based QR Code Generator** that creates **high-error-correction QR codes** with a custom logo embedded in the center.

Hosted on **Render (Free Web Service)** and built using Python, Flask, Pillow, and the qrcode library.

---

## ✨ Features

- Generate QR codes from URLs
- Embed a custom logo in the center
- High error correction (Level H)
- Automatic URL normalization (`example.com` → `https://example.com`)
- PNG image download
- Image validation and size limits
- Health check endpoint
- REST API backend
- Lightweight and easy to deploy

---

## 📸 Screenshots

### Home Page

> *(Insert screenshot here)*

<br>

### Generated QR Code

> *(Insert screenshot here)*

<br>

### Mobile View

> *(Insert screenshot here)*

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend |
| Flask | Web Framework |
| Flask-CORS | Cross-Origin Support |
| qrcode | QR Code Generation |
| Pillow | Image Processing |
| Gunicorn | Production WSGI Server |
| Render | Cloud Hosting |

---

## 📦 Requirements

```text
flask==3.0.3
flask-cors==4.0.0
qrcode[pil]==7.4.2
pillow==10.4.0
python-dotenv==1.0.1
gunicorn==23.0.0
```

Install everything using:

```bash
pip install -r requirements.txt
```

---

## 🚀 Running Locally

Clone the repository:

```bash
git clone https://github.com/yourusername/your-repository.git
```

Move into the project:

```bash
cd your-repository
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the Flask server:

```bash
python app.py
```

The application will run on:

```
http://localhost:3000
```

---

## 🌐 API

### Generate QR Code

**POST**

```
/generate_qr
```

### Request Body

```json
{
    "link": "https://example.com",
    "image": "Base64EncodedImage"
}
```

### Response

Returns:

- PNG QR Code image
- Download filename:
  ```
  qr_with_logo.png
  ```

---

## ❤️ QR Code Specifications

The application generates QR Codes with:

| Setting | Value |
|---------|------|
| Error Correction | H (Highest - ~30% recovery) |
| Box Size | 10 |
| Border | 4 |
| Output Format | PNG |
| Logo Size | 25% of QR Width |

Using **Level H** error correction allows the QR code to remain scannable even after placing a logo in the center.

---

## 📋 Supported Image Formats

Logo uploads support:

- PNG
- JPEG
- WEBP

Maximum image size:

- 2000 × 2000 pixels

---

## 🔍 URL Handling

The backend automatically:

- Trims whitespace
- Accepts URLs with or without protocol
- Converts:

```
google.com
```

into

```
https://google.com
```

before generating the QR code.

---

## ❤️ Health Endpoint

```
GET /health
```

Example response:

```json
{
    "status": "healthy",
    "service": "qr-generator",
    "version": "1.0.0"
}
```

Useful for Render health checks and uptime monitoring.

---

## 📁 Project Structure

```
project/
│
├── templates/
│   └── index.html
│
├── static/
│
├── app.py
├── requirements.txt
├── render.yaml (optional)
└── README.md
```

---

## ☁️ Deployment

This project is deployed using **Render Free Web Service**.

Production server:

- Gunicorn
- Flask
- Automatic HTTPS
- Health endpoint available

Example start command:

```bash
gunicorn app:app
```

---

## 🔒 Validation & Security

The backend includes:

- Request validation
- URL validation
- Image format validation
- Maximum upload size limits
- Error handling with JSON responses
- Logging for request monitoring

---

## 📄 License

This project is available under the MIT License.

Feel free to use, modify, and improve it.

---

## 👨‍💻 Author

Developed using **Python**, **Flask**, and **Pillow**.

If you found this project useful, consider giving it a ⭐ on GitHub.