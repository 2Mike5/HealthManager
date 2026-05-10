from flask import Flask, request
from models import init_db
from routes import api
from auth import auth_bp
from routes_weight import weight_bp
from routes_diet import diet_bp, food_bp
from food_seed_data import seed_food_database

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
        response = app.make_default_options_response()
        return response

app.register_blueprint(api)
app.register_blueprint(auth_bp)
app.register_blueprint(weight_bp)
app.register_blueprint(diet_bp)
app.register_blueprint(food_bp)

@app.route('/')
def index():
    return {'code': 200, 'message': 'Health Tracker API is running'}

if __name__ == '__main__':
    init_db()
    seed_food_database()
    app.run(host='0.0.0.0', port=5001, threaded=True, debug=True)