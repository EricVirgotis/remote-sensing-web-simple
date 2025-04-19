# -*- coding: utf-8 -*-
"""
遥感智能分类分析系统 - 算法服务

提供遥感影像分类、模型训练等功能的Flask API服务
"""

import os
import logging
from datetime import datetime # Add this import
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO # 添加 SocketIO 导入

# 导入路由模块
from routes.classify import classify_bp
from routes.model import model_bp
from routes.train import train_bp
from utils.db_utils import init_db

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app) # 允许所有来源的跨域请求

# 初始化 SocketIO
socketio = SocketIO(app, cors_allowed_origins="*") # 允许所有来源连接

# 配置日志
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 注册蓝图
app.register_blueprint(classify_bp, url_prefix='/api/classify')
app.register_blueprint(model_bp, url_prefix='/api/model')
app.register_blueprint(train_bp, url_prefix='/api/train')

def legacy_train_health_check():
    return jsonify({
        'status': 'ok',
        'service': 'algorithm-service',
        'version': '1.0.0'
    })

# 健康检查路由
@app.route('/api/health/health_check', methods=['GET'])
def health_check():
    # 这里可以添加更复杂的健康检查逻辑，例如检查数据库连接、依赖服务等
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested URL was not found on the server.'
    }), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An internal server error occurred.'
    }), 500

# 启动服务
if __name__ == '__main__':
    # 初始化数据库
    init_db()
    # 使用 socketio.run() 启动应用，以便支持 WebSocket
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    # app.run(host='0.0.0.0', port=5000, debug=True)