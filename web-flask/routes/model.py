# -*- coding: utf-8 -*-
"""
模型管理路由模块

处理模型相关请求
"""

import os
import logging
import json
import time
import shutil
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from algo.model_loader import get_available_models, get_default_model, load_model

logger = logging.getLogger(__name__)

# 创建蓝图
model_bp = Blueprint('model', __name__)

# 模型目录
MODEL_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / '../models'
os.makedirs(MODEL_DIR, exist_ok=True)

# 模型配置文件
MODEL_CONFIG_PATH = MODEL_DIR / 'model_config.json'

def save_model_config(config):
    """
    保存模型配置
    
    Args:
        config (dict): 模型配置
    """
    with open(MODEL_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def load_model_config():
    """
    加载模型配置
    
    Returns:
        dict: 模型配置
    """
    if not os.path.exists(MODEL_CONFIG_PATH):
        return {'default_model': None}
    
    with open(MODEL_CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

@model_bp.route('/list', methods=['GET'])
def list_models():
    """
    获取可用模型列表
    
    Returns:
        JSON: 模型列表
    """
    try:
        # 获取可用模型
        available_models = get_available_models()
        default_model = get_default_model()
        
        # 获取模型详细信息
        models_info = []
        for model_name in available_models:
            model_path = MODEL_DIR / f"{model_name}.pt"
            if not model_path.exists():
                model_path = MODEL_DIR / f"{model_name}.pth"
            
            # 获取文件信息
            file_info = {
                'name': model_name,
                'path': str(model_path),
                'size': os.path.getsize(model_path),
                'created_time': os.path.getctime(model_path),
                'is_default': model_name == default_model
            }
            
            # 获取训练结果信息
            result_path = Path(os.path.dirname(os.path.abspath(__file__))) / f"../train_results/{model_name}_result.json"
            if os.path.exists(result_path):
                with open(result_path, 'r', encoding='utf-8') as f:
                    training_info = json.load(f)
                file_info['training_info'] = training_info
            
            models_info.append(file_info)
        
        return jsonify({
            'status': 'success',
            'data': {
                'models': models_info,
                'default_model': default_model
            }
        })
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取模型列表失败: {str(e)}"
        }), 500

@model_bp.route('/upload', methods=['POST'])
def upload_model():
    """
    上传模型文件
    
    Returns:
        JSON: 上传结果
    """
    try:
        # 检查是否有文件上传
        if 'model' not in request.files:
            return jsonify({
                'code': 400,
                'message': '没有上传文件'
            })
        
        file = request.files['model']
        if file.filename == '':
            return jsonify({
                'code': 400,
                'message': '没有选择文件'
            })
        
        # 检查文件类型
        if not file.filename.endswith(('.pt', '.pth', '.h5')):
            return jsonify({
                'code': 400,
                'message': '不支持的文件格式，仅支持.pt、.pth或.h5格式'
            })
        
        # 获取模型名称
        model_name = request.form.get('model_name', None)
        if not model_name:
            # 使用文件名作为模型名称
            model_name = os.path.splitext(secure_filename(file.filename))[0]
        else:
            # 安全处理模型名称
            model_name = secure_filename(model_name)
        
        # 保存模型文件
        file_ext = os.path.splitext(file.filename)[1].lower()
        model_path = MODEL_DIR / f"{model_name}{file_ext}"
        file.save(model_path)
        
        # 设置为默认模型（如果请求中指定）
        set_as_default = request.form.get('set_as_default', 'false').lower() == 'true'
        if set_as_default:
            config = load_model_config()
            config['default_model'] = model_name
            save_model_config(config)
        
        return jsonify({
            'status': 'success',
            'message': '模型上传成功',
            'data': {
                'model_name': model_name,
                'model_path': str(model_path),
                'is_default': set_as_default
            }
        })
    except Exception as e:
        logger.error(f"上传模型失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"上传模型失败: {str(e)}"
        }), 500

@model_bp.route('/set_default', methods=['POST'])
def set_default_model():
    """
    设置默认模型
    
    Returns:
        JSON: 设置结果
    """
    try:
        # 获取请求数据
        data = request.json
        if not data or 'model_name' not in data:
            return jsonify({
                'status': 'error',
                'message': '请求数据无效，缺少model_name字段'
            }), 400
        
        model_name = data['model_name']
        
        # 检查模型是否存在
        available_models = get_available_models()
        if model_name not in available_models:
            return jsonify({
                'status': 'error',
                'message': f"模型 {model_name} 不存在"
            }), 404
        
        # 更新配置
        config = load_model_config()
        config['default_model'] = model_name
        save_model_config(config)
        
        return jsonify({
            'status': 'success',
            'message': f"已将 {model_name} 设置为默认模型"
        })
    except Exception as e:
        logger.error(f"设置默认模型失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"设置默认模型失败: {str(e)}"
        }), 500

@model_bp.route('/delete/<model_name>', methods=['DELETE'])
def delete_model(model_name):
    """
    删除模型
    
    Args:
        model_name (str): 模型名称
        
    Returns:
        JSON: 删除结果
    """
    try:
        # 检查模型是否存在
        model_path = MODEL_DIR / f"{model_name}.pt"
        if not model_path.exists():
            model_path = MODEL_DIR / f"{model_name}.pth"
        
        if not model_path.exists():
            return jsonify({
                'status': 'error',
                'message': f"模型 {model_name} 不存在"
            }), 404
        
        # 检查是否为默认模型
        default_model = get_default_model()
        if model_name == default_model:
            return jsonify({
                'status': 'error',
                'message': f"无法删除默认模型 {model_name}，请先设置其他模型为默认"
            }), 400
        
        # 删除模型文件
        os.remove(model_path)
        
        # 删除训练结果文件（如果存在）
        result_path = Path(os.path.dirname(os.path.abspath(__file__))) / f"../train_results/{model_name}_result.json"
        if os.path.exists(result_path):
            os.remove(result_path)
        
        return jsonify({
            'status': 'success',
            'message': f"模型 {model_name} 已删除"
        })
    except Exception as e:
        logger.error(f"删除模型失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"删除模型失败: {str(e)}"
        }), 500

@model_bp.route('/info/<model_name>', methods=['GET'])
def get_model_info(model_name):
    """
    获取模型详细信息
    
    Args:
        model_name (str): 模型名称
        
    Returns:
        JSON: 模型信息
    """
    try:
        # 检查模型是否存在
        model_path = MODEL_DIR / f"{model_name}.pt"
        if not model_path.exists():
            model_path = MODEL_DIR / f"{model_name}.pth"
        
        if not model_path.exists():
            return jsonify({
                'status': 'error',
                'message': f"模型 {model_name} 不存在"
            }), 404
        
        # 获取文件信息
        file_info = {
            'name': model_name,
            'path': str(model_path),
            'size': os.path.getsize(model_path),
            'created_time': os.path.getctime(model_path),
            'is_default': model_name == get_default_model()
        }
        
        # 获取训练结果信息
        result_path = Path(os.path.dirname(os.path.abspath(__file__))) / f"../train_results/{model_name}_result.json"
        if os.path.exists(result_path):
            with open(result_path, 'r', encoding='utf-8') as f:
                training_info = json.load(f)
            file_info['training_info'] = training_info
        
        return jsonify({
            'status': 'success',
            'data': file_info
        })
    except Exception as e:
        logger.error(f"获取模型信息失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取模型信息失败: {str(e)}"
        }), 500