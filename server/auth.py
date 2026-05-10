"""
auth.py — 用户认证模块
JWT 登录/注册/个人信息，密码哈希
"""
from datetime import datetime, timedelta
from functools import wraps
import jwt
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import get_db

SECRET_KEY = 'health-tracker-jwt-secret-key-2026-xxxx'

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def generate_token(user_id, username):
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'code': 401, 'data': None, 'message': '未登录或令牌已过期'}), 401
        token = auth_header[7:]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user_id = payload['user_id']
            request.username = payload['username']
        except jwt.ExpiredSignatureError:
            return jsonify({'code': 401, 'data': None, 'message': '令牌已过期，请重新登录'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'code': 401, 'data': None, 'message': '无效的令牌'}), 401
        return f(*args, **kwargs)
    return decorated


def success(data=None, message='ok'):
    return jsonify({'code': 200, 'data': data, 'message': message})


def error(code, message):
    return jsonify({'code': code, 'data': None, 'message': message}), code


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password', '')
    nickname = (data.get('nickname') or '').strip() or username

    if not username or len(username) < 2:
        return error(400, '用户名至少2个字符')
    if len(password) < 6:
        return error(400, '密码至少6个字符')

    db = get_db()
    existing = db.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    if existing:
        db.close()
        return error(409, '用户名已存在')

    password_hash = generate_password_hash(password)
    now = datetime.now().isoformat()
    cursor = db.execute(
        "INSERT INTO users (username, password_hash, nickname, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (username, password_hash, nickname, now, now)
    )
    db.commit()
    user_id = cursor.lastrowid
    token = generate_token(user_id, username)
    db.close()
    return success({
        'token': token,
        'user': {'id': user_id, 'username': username, 'nickname': nickname}
    }, '注册成功'), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password', '')

    if not username or not password:
        return error(400, '用户名和密码不能为空')

    db = get_db()
    row = db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    db.close()

    if row is None or not check_password_hash(row['password_hash'], password):
        return error(401, '用户名或密码错误')

    token = generate_token(row['id'], row['username'])
    return success({
        'token': token,
        'user': {
            'id': row['id'], 'username': row['username'],
            'nickname': row['nickname'], 'avatar': row['avatar'],
            'height': row['height'], 'target_weight': row['target_weight']
        }
    })


@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE id = ?", (request.user_id,)).fetchone()
    db.close()
    if row is None:
        return error(404, '用户不存在')
    return success({
        'id': row['id'], 'username': row['username'],
        'nickname': row['nickname'], 'avatar': row['avatar'],
        'height': row['height'], 'target_weight': row['target_weight'],
        'created_at': row['created_at']
    })


@auth_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    data = request.get_json(silent=True) or {}
    allowed = {'nickname', 'avatar', 'height', 'target_weight'}
    updates = {k: v for k, v in data.items() if k in allowed and v is not None}
    if not updates:
        return error(400, '没有可更新的字段')
    updates['updated_at'] = datetime.now().isoformat()

    db = get_db()
    cols = ', '.join(f"{k} = ?" for k in updates)
    db.execute(
        f"UPDATE users SET {cols} WHERE id = ?",
        list(updates.values()) + [request.user_id]
    )
    db.commit()
    row = db.execute("SELECT * FROM users WHERE id = ?", (request.user_id,)).fetchone()
    db.close()
    return success({
        'id': row['id'], 'username': row['username'],
        'nickname': row['nickname'], 'avatar': row['avatar'],
        'height': row['height'], 'target_weight': row['target_weight']
    }, '更新成功')
