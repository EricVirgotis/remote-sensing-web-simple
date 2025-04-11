# -*- coding: utf-8 -*-
"""
分类路由模块

处理遥感影像分类请求
"""

import os
import logging
import json
import time
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from algo.classifier import RemoteSensingClassifier
from algo.model_loader import get_available_models, get_default_model

logger = logging.getLogger(__name__)

# 创建蓝图
classify_bp = Blueprint('classify', __name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'.tif', '.tiff', '.img', '.jpg', '.jpeg', '.png'}

# 结果保存目录
RESULT_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / '../results'
os.makedirs(RESULT_DIR, exist_ok=True)

def allowed_file(filename):
    """
    检查文件扩展名是否允许
    
    Args:
        filename (str): 文件名
        
    Returns:
        bool: 是否允许
    """
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

@classify_bp.route('/info', methods=['GET'])
def classify_info():
    """
    获取分类服务信息
    
    Returns:
        JSON: 分类服务信息
    """
    try:
        # 获取可用模型
        available_models = get_available_models()
        default_model = get_default_model()
        
        return jsonify({
            'status': 'success',
            'data': {
                'available_models': available_models,
                'default_model': default_model,
                'allowed_extensions': list(ALLOWED_EXTENSIONS)
            }
        })
    except Exception as e:
        logger.error(f"获取分类服务信息失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取分类服务信息失败: {str(e)}"
        }), 500

@classify_bp.route('/predict', methods=['POST'])
def predict():
    """
    对上传的遥感影像进行分类预测
    
    Returns:
        JSON: 预测结果
    """
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': '没有上传文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': '没有选择文件'
            }), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': f"不支持的文件类型，允许的类型: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
        
        # 获取模型名称
        model_name = request.form.get('model_name', None)
        
        # 保存上传的文件
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        save_path = RESULT_DIR / f"{timestamp}_{filename}"
        file.save(save_path)
        
        # 创建分类器并预测
        classifier = RemoteSensingClassifier(model_name=model_name)
        result = classifier.predict(str(save_path))
        
        # 添加文件信息
        result['file_info'] = {
            'original_filename': file.filename,
            'saved_filename': save_path.name,
            'file_size': os.path.getsize(save_path),
            'timestamp': timestamp
        }
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        logger.error(f"预测失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"预测失败: {str(e)}"
        }), 500

@classify_bp.route('/batch', methods=['POST'])
def batch_predict():
    """
    批量预测多个遥感影像
    
    请求体应包含文件路径列表
    
    Returns:
        JSON: 预测结果列表
    """
    try:
        # 获取请求数据
        data = request.json
        if not data or 'file_paths' not in data:
            return jsonify({
                'status': 'error',
                'message': '请求数据无效，缺少file_paths字段'
            }), 400
        
        file_paths = data['file_paths']
        if not isinstance(file_paths, list) or len(file_paths) == 0:
            return jsonify({
                'status': 'error',
                'message': 'file_paths必须是非空列表'
            }), 400
        
        # 获取模型名称
        model_name = data.get('model_name', None)
        
        # 创建分类器并批量预测
        classifier = RemoteSensingClassifier(model_name=model_name)
        results = classifier.predict_batch(file_paths)
        
        return jsonify({
            'status': 'success',
            'data': results
        })
    except Exception as e:
        logger.error(f"批量预测失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"批量预测失败: {str(e)}"
        }), 500

@classify_bp.route('/segment', methods=['POST'])
def segment():
    """
    对大型遥感影像进行分割分类
    
    Returns:
        JSON: 分割分类结果
    """
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': '没有上传文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': '没有选择文件'
            }), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': f"不支持的文件类型，允许的类型: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
        
        # 获取参数
        model_name = request.form.get('model_name', None)
        tile_size = int(request.form.get('tile_size', 256))
        overlap = int(request.form.get('overlap', 32))
        
        # 保存上传的文件
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        save_path = RESULT_DIR / f"{timestamp}_{filename}"
        file.save(save_path)
        
        # 创建分类器并分割分类
        classifier = RemoteSensingClassifier(model_name=model_name)
        result = classifier.segment(str(save_path), tile_size=tile_size, overlap=overlap)
        
        # 添加文件信息
        result['file_info'] = {
            'original_filename': file.filename,
            'saved_filename': save_path.name,
            'file_size': os.path.getsize(save_path),
            'timestamp': timestamp
        }
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        logger.error(f"分割分类失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"分割分类失败: {str(e)}"
        }), 500