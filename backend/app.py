import os
import uuid
from datetime import datetime, timedelta

from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask_cors import CORS

from models import db, Admin, Problem

from dotenv import load_dotenv
load_dotenv()

FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret')
JWT_SECRET = os.getenv('JWT_SECRET', 'jwt-secret')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'mysql+pymysql://root:pass@localhost/toilet_tracker')

ALLOWED_EXT = {'png','jpg','jpeg','gif'}

app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.init_app(app)
CORS(app, supports_credentials=True)

def create_admin_jwt(admin_id, username):
    payload = {
        'sub': admin_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=8)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def decode_jwt(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except Exception:
        return None

def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error':'missing token'}), 401
        token = auth.split(' ',1)[1]
        payload = decode_jwt(token)
        if not payload:
            return jsonify({'error':'invalid or expired token'}), 401
        admin = Admin.query.get(payload.get('sub'))
        if not admin:
            return jsonify({'error':'admin not found'}), 401
        request.admin = admin
        return fn(*args, **kwargs)
    return wrapper


@app.route('/api/problems', methods=['GET'])
def list_problems():
    q = Problem.query.order_by(Problem.created_at.desc()).all()
    out = []
    for p in q:
        out.append({
            'id': p.id,
            'room_id': p.room_id,
            'category': p.category,
            'user_name': p.user_name,
            'user_status': p.user_status,
            'problem_desc': p.problem_desc,
            'img_path': p.img_path,
            'status': p.status,
            'timestamp': p.created_at.isoformat() if p.created_at else None,
        })
    return jsonify(out)

@app.route('/api/problems', methods=['POST'])
def create_problem():
    data = dict(request.form)
    category = data.get('category')
    room_id = data.get('room_id') or data.get('room-id')
    user_name = data.get('user_name') or data.get('user-name')
    user_status = data.get('user_status') or data.get('user-status')
    user_phone = data.get('user_phone') or data.get('user-phone')
    user_email = data.get('user_email') or data.get('user-email')
    problem_desc = data.get('problem_desc') or data.get('problem-desc')
    img_path = None
    if 'image' in request.files:
        f = request.files['image']
        if f and '.' in f.filename and f.filename.rsplit('.',1)[1].lower() in ALLOWED_EXT:
            filename = secure_filename(f.filename)
            unique = f"{uuid.uuid4().hex}_{filename}"
            full = os.path.join(app.config['UPLOAD_FOLDER'], unique)
            f.save(full)
            img_path = f"/uploads/{unique}"
    p = Problem(
        room_id=room_id,
        category=category,
        user_name=user_name,
        user_status=user_status,
        user_phone=user_phone,
        user_email=user_email,
        problem_desc=problem_desc,
        img_path=img_path,
        status='pending'
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({'id': p.id, 'message': 'created'}), 201

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
# Admin endpoint
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    body = request.json or {}
    username = body.get('username')
    password = body.get('password')
    if not username or not password:
        return jsonify({'error':'missing credentials'}), 400
    admin = Admin.query.filter_by(username=username).first()
    if not admin:
        return jsonify({'error':'invalid credentials'}), 401
    if not check_password_hash(admin.password_hash, password):
        return jsonify({'error':'invalid credentials'}), 401
    token = create_admin_jwt(admin.id, admin.username)
    return jsonify({'token': token})

@app.route('/api/admin/problems', methods=['POST'])
@admin_required
def admin_create_problem():
    data = dict(request.form)
    category = data.get('category')
    room_id = data.get('room_id')
    user_name = data.get('user_name')
    user_status = data.get('user_status')
    user_phone = data.get('user_phone')
    user_email = data.get('user_email')
    problem_desc = data.get('problem_desc')
    img_path = None

    if 'image' in request.files:
        f = request.files['image']
        if f and '.' in f.filename and f.filename.rsplit('.',1)[1].lower() in ALLOWED_EXT:
            filename = secure_filename(f.filename)
            unique = f"{uuid.uuid4().hex}_{filename}"
            full = os.path.join(app.config['UPLOAD_FOLDER'], unique)
            f.save(full)
            img_path = f"/uploads/{unique}"

    p = Problem(
        room_id=room_id,
        category=category,
        user_name=user_name,
        user_status=user_status,
        user_phone=user_phone,
        user_email=user_email,
        problem_desc=problem_desc,
        img_path=img_path,
        status=data.get('status', 'pending')
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({'id': p.id, 'message': 'created by admin'}), 201

@app.route('/api/admin/problems', methods=['GET'])
@admin_required
def admin_list_problems():
    q = Problem.query.order_by(Problem.created_at.desc()).all()
    out = []
    for p in q:
        out.append({
            'id': p.id,
            'room_id': p.room_id,
            'category': p.category,
            'user_name': p.user_name,
            'user_status': p.user_status,
            'user_phone': p.user_phone,
            'user_email': p.user_email,
            'problem_desc': p.problem_desc,
            'img_path': p.img_path,
            'status': p.status,
            'timestamp': p.created_at.isoformat() if p.created_at else None
        })
    return jsonify(out)

@app.route('/api/admin/problems/<int:problem_id>', methods=['PUT'])
@admin_required
def admin_update_problem(problem_id):
    p = Problem.query.get(problem_id)
    if not p:
        return jsonify({'error':'not found'}), 404

    # อ่านข้อมูลจาก JSON 
    data = request.get_json(silent=True)
    if not data:
        data = dict(request.form) if request.form else {}

    # อัปเดตฟิลด์ที่มีใน data (เช็ค presence ของ key โดยตรง)
    for k in ['room_id','category','user_name','user_status','user_phone','user_email','problem_desc','status']:
        if k in data:
            setattr(p, k, data[k])

    # ถ้ามีไฟล์รูป ให้บันทึกและอัปเดต p.img_path
    if 'image' in request.files:
        f = request.files['image']
        if f and '.' in f.filename and f.filename.rsplit('.',1)[1].lower() in ALLOWED_EXT:
            filename = secure_filename(f.filename)
            unique = f"{uuid.uuid4().hex}_{filename}"
            full = os.path.join(app.config['UPLOAD_FOLDER'], unique)
            f.save(full)
            p.img_path = f"/uploads/{unique}"

    # ปิดท้ายด้วย commit เสมอ
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'db commit failed', 'detail': str(e)}), 500

    return jsonify({'message':'updated','id':p.id})

@app.route('/api/admin/problems/<int:problem_id>', methods=['DELETE'])
@admin_required
def admin_delete_problem(problem_id):
    p = Problem.query.get(problem_id)
    if not p:
        return jsonify({'error':'not found'}), 404
    db.session.delete(p)
    db.session.commit()
    return jsonify({'message':'deleted','id':problem_id})

@app.before_request
def init_db():
    if not Admin.query.first():
        default_username = "hatyairat_toilet"
        default_password = "toilettracker_admin_69"
        h = generate_password_hash(default_password)
        admin = Admin(username=default_username, password_hash=h)
        db.session.add(admin)
        db.session.commit()
        print(f"[INFO] Default admin created: {default_username}/{default_password}")

@app.route('/')
def home():
    return send_from_directory("../frontend", "index.html")

@app.route('/login')
def login_page():
    return send_from_directory("../frontend", "login.html")

@app.route('/admin')
def admin_page():
    return send_from_directory("../frontend", "admin.html")

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory("../frontend", path)

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
