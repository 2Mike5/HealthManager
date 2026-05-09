from flask import Flask
from models import init_db
from routes import api

app = Flask(__name__)

# ---------- 手动 CORS 处理，不用 flask_cors ----------
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# 手动处理 OPTIONS 预检请求（全局截获）
@app.before_request
def handle_options_request():
    if request.method == 'OPTIONS':
        # 直接返回一个带有正确 CORS 头的空响应
        response = app.make_default_options_response()
        # 上面的 after_request 会自动再添加一遍头，最终返回 200 OK
        return response

app.register_blueprint(api)

@app.route('/')
def index():
    return {'code': 200, 'message': 'Health Tracker API is running'}

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, threaded=True, debug=True)