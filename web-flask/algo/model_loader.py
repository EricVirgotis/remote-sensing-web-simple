# -*- coding: utf-8 -*-
"""
模型加载器

负责加载和管理预训练的遥感影像分类模型
"""

import os
import logging
import torch
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# 模型存储路径
MODEL_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / '../models'

# 全局模型缓存
model_cache = {}

class ModelNotFoundError(Exception):
    """模型未找到异常"""
    pass

def get_available_models():
    """
    获取所有可用的模型列表
    
    Returns:
        list: 模型名称列表
    """
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR, exist_ok=True)
        logger.warning(f"模型目录不存在，已创建: {MODEL_DIR}")
        return []
    
    # 查找所有.pt、.pth或.h5文件
    model_files = list(MODEL_DIR.glob('*.pt')) + list(MODEL_DIR.glob('*.pth')) + list(MODEL_DIR.glob('*.h5'))
    return [model.stem for model in model_files]

def load_model(model_name):
    """
    加载指定名称的模型
    
    Args:
        model_name (str): 模型名称
        
    Returns:
        model: 加载的模型对象
        
    Raises:
        ModelNotFoundError: 当模型不存在时抛出
    """
    # 检查模型是否已缓存
    if model_name in model_cache:
        logger.info(f"从缓存加载模型: {model_name}")
        return model_cache[model_name]
    
    # 构建模型文件路径并尝试不同格式
    for ext in ['.pt', '.pth', '.h5']:
        model_path = MODEL_DIR / f"{model_name}{ext}"
        if model_path.exists():
            break
    else:
        raise ModelNotFoundError(f"模型 {model_name} 不存在")
    
    try:
        # 加载模型
        logger.info(f"加载模型: {model_path}")
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 根据文件扩展名选择加载方式
        if model_path.suffix == '.h5':
            import tensorflow as tf
            model = tf.keras.models.load_model(str(model_path))
            # TensorFlow模型不需要显式设置eval模式
        else:
            model = torch.load(model_path, map_location=device)
            # PyTorch模型需要设置eval模式
            model.eval()
        
        # 缓存模型
        model_cache[model_name] = model
        
        return model
    except Exception as e:
        logger.error(f"加载模型 {model_name} 失败: {str(e)}")
        raise

def get_default_model():
    """
    获取默认模型
    
    Returns:
        str: 默认模型名称
    """
    available_models = get_available_models()
    if not available_models:
        return None
    
    # 读取默认模型配置或使用第一个可用模型
    # TODO: 从配置文件读取默认模型
    return available_models[0]

def load_default_models():
    """
    预加载默认模型到内存
    """
    default_model = get_default_model()
    if default_model:
        try:
            load_model(default_model)
            logger.info(f"默认模型 {default_model} 加载成功")
        except Exception as e:
            logger.error(f"加载默认模型失败: {str(e)}")
    else:
        logger.warning("没有可用的默认模型")