# -*- coding: utf-8 -*-
"""
遥感智能分类分析系统 - 算法服务

提供遥感影像分类、模型训练等功能的Flask API服务
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# 导入路由模块
from routes.classify import classify_bp
from routes.train import train_bp
from routes.model import model_bp

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用CORS支持跨域请求

# 注册蓝图
app.register_blueprint(classify_bp, url_prefix='/api/classify')
app.register_blueprint(train_bp, url_prefix='/api/train')

def legacy_train_health_check():
    return jsonify({
        'status': 'ok',
        'service': 'algorithm-service',
        'version': '1.0.0'
    })
app.register_blueprint(model_bp, url_prefix='/api/model')

# 健康检查路由
@app.route('/api/health/health_check', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'service': 'algorithm-service',
        'version': '1.0.0'
    })

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
    # 预热模型
    from algo.model_loader import load_default_models
    logger.info("正在预热模型...")
    load_default_models()
    logger.info("模型预热完成")
    
    # 启动Flask应用
    port = int(os.environ.get('PORT', 5000))
    app.run(host='localhost', port=port, debug=False, threaded=True, use_reloader=False)