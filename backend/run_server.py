import os
import socket
import threading
import qrcode
from flask import Flask, send_from_directory
from app import app  # ดึง Flask app เดิมจาก app.py มาใช้

# === CONFIG ===
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
FRONTEND_PORT = 8000
BACKEND_PORT = 5000

# === สร้าง Flask app เสิร์ฟ frontend ===
frontend = Flask("frontend", static_folder=FRONTEND_DIR)

@frontend.route("/", defaults={"path": "index.html"})
@frontend.route("/<path:path>")
def serve_frontend(path):
    return send_from_directory(FRONTEND_DIR, path)

# === Utility: หา local IP ของเครื่อง ===
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

# === Run Flask backend (app.py) ===
def run_backend():
    app.run(host="0.0.0.0", port=BACKEND_PORT, debug=False)

# === Run frontend static server ===
def run_frontend():
    frontend.run(host="0.0.0.0", port=FRONTEND_PORT, debug=False)

if __name__ == "__main__":
    local_ip = get_local_ip()
    backend_url = f"http://{local_ip}:{BACKEND_PORT}"
    frontend_url = f"http://{local_ip}:{FRONTEND_PORT}"

    print(f"\n🚀 Backend running at: {backend_url}")
    print(f"🌐 Frontend running at: {frontend_url}")

    # สร้าง QR Code สำหรับ frontend
    img = qrcode.make(frontend_url)
    qr_path = "qrcode.png"
    img.save(qr_path)
    print(f"📱 QR Code generated: {qr_path}")

    # รัน backend + frontend พร้อมกัน
    threading.Thread(target=run_backend, daemon=True).start()
    run_frontend()

