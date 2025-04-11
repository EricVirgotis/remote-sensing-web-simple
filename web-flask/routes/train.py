# -*- coding: utf-8 -*-
"""
训练路由模块

处理模型训练请求
"""

import os
import logging
import json
import time
import shutil
import zipfile
import random
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from algo.trainer import ModelTrainer

logger = logging.getLogger(__name__)

# 创建蓝图
train_bp = Blueprint('train', __name__)

# 数据集目录
DATASET_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / '../datasets'
os.makedirs(DATASET_DIR, exist_ok=True)

# 训练结果目录
TRAIN_RESULT_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / '../train_results'
os.makedirs(TRAIN_RESULT_DIR, exist_ok=True)

@train_bp.route('/upload_dataset', methods=['POST'])
def upload_dataset():
    """
    上传数据集
    
    支持ZIP格式的数据集文件
    
    Returns:
        JSON: 上传结果
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
        if not file.filename.lower().endswith('.zip'):
            return jsonify({
                'status': 'error',
                'message': '只支持ZIP格式的数据集文件'
            }), 400
        
        # 获取数据集名称
        dataset_name = request.form.get('dataset_name', None)
        if not dataset_name:
            # 使用时间戳作为数据集名称
            dataset_name = f"dataset_{int(time.time())}"
        else:
            # 安全处理数据集名称
            dataset_name = secure_filename(dataset_name)
        
        # 创建数据集目录
        dataset_dir = DATASET_DIR / dataset_name
        if os.path.exists(dataset_dir):
            # 如果目录已存在，先删除
            shutil.rmtree(dataset_dir)
        os.makedirs(dataset_dir, exist_ok=True)
        
        # 保存上传的文件
        zip_path = dataset_dir / 'dataset.zip'
        file.save(zip_path)
        
        # 解压数据集
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dataset_dir)
        
        # 删除ZIP文件
        os.remove(zip_path)
        
        # 创建训练集和验证集目录
        train_dir = dataset_dir / 'train'
        val_dir = dataset_dir / 'val'
        os.makedirs(train_dir, exist_ok=True)
        os.makedirs(val_dir, exist_ok=True)
        
        # 遍历解压后的数据集目录
        for class_dir in dataset_dir.iterdir():
            if class_dir.is_dir() and class_dir.name not in ['train', 'val']:
                # 创建对应的训练集和验证集子目录
                train_class_dir = train_dir / class_dir.name
                val_class_dir = val_dir / class_dir.name
                os.makedirs(train_class_dir, exist_ok=True)
                os.makedirs(val_class_dir, exist_ok=True)
                
                # 获取该类别下的所有图片
                images = [f for f in class_dir.iterdir() if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
                random.shuffle(images)  # 随机打乱
                
                # 按7:3比例划分
                split_idx = int(len(images) * 0.7)
                train_images = images[:split_idx]
                val_images = images[split_idx:]
                
                # 移动文件到对应目录
                for img in train_images:
                    shutil.move(str(img), str(train_class_dir / img.name))
                for img in val_images:
                    shutil.move(str(img), str(val_class_dir / img.name))
                
                # 删除原始类别目录
                shutil.rmtree(class_dir)
        
        dataset_info = {
            'dataset_name': dataset_name,
            'dataset_path': str(dataset_dir),
            'has_train': True,
            'has_val': True,
            'classes': []
        }
        
        # 获取类别信息
        if os.path.exists(train_dir):
            classes = [d.name for d in train_dir.iterdir() if d.is_dir()]
            dataset_info['classes'] = classes
            
            # 统计每个类别的样本数量
            class_counts = {}
            for cls in classes:
                class_dir = train_dir / cls
                class_counts[cls] = len([f for f in class_dir.iterdir() if f.is_file()])
            dataset_info['class_counts'] = class_counts
        
        return jsonify({
            'status': 'success',
            'message': '数据集上传成功',
            'data': dataset_info
        })
    except Exception as e:
        logger.error(f"上传数据集失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"上传数据集失败: {str(e)}"
        }), 500

@train_bp.route('/list_datasets', methods=['GET'])
def list_datasets():
    """
    获取可用数据集列表
    
    Returns:
        JSON: 数据集列表
    """
    try:
        datasets = []
        
        # 遍历数据集目录
        for dataset_dir in DATASET_DIR.iterdir():
            if dataset_dir.is_dir():
                # 检查数据集结构
                train_dir = dataset_dir / 'train'
                val_dir = dataset_dir / 'val'
                test_dir = dataset_dir / 'test'
                
                dataset_info = {
                    'dataset_name': dataset_dir.name,
                    'dataset_path': str(dataset_dir),
                    'has_train': os.path.exists(train_dir),
                    'has_val': os.path.exists(val_dir),
                    'has_test': os.path.exists(test_dir),
                    'classes': []
                }
                
                # 获取类别信息
                if os.path.exists(train_dir):
                    classes = [d.name for d in train_dir.iterdir() if d.is_dir()]
                    dataset_info['classes'] = classes
                    
                    # 统计每个类别的样本数量
                    class_counts = {}
                    for cls in classes:
                        class_dir = train_dir / cls
                        class_counts[cls] = len([f for f in class_dir.iterdir() if f.is_file()])
                    dataset_info['class_counts'] = class_counts
                
                datasets.append(dataset_info)
        
        return jsonify({
            'status': 'success',
            'data': datasets
        })
    except Exception as e:
        logger.error(f"获取数据集列表失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取数据集列表失败: {str(e)}"
        }), 500

@train_bp.route('/start', methods=['POST'])
def start_training():
    """
    开始模型训练
    
    Returns:
        JSON: 训练任务信息
    """
    try:
        # 获取请求数据
        data = request.json
        if not data:
            return jsonify({
                'status': 'error',
                'message': '请求数据无效'
            }), 400
        
        # 获取参数
        dataset_name = data.get('dataset_name')
        model_name = data.get('model_name')
        epochs = data.get('epochs', 30)
        batch_size = data.get('batch_size', 32)
        
        if not dataset_name:
            return jsonify({
                'status': 'error',
                'message': '缺少数据集名称'
            }), 400
        
        if not model_name:
            return jsonify({
                'status': 'error',
                'message': '缺少模型名称'
            }), 400
        
        # 检查数据集是否存在
        dataset_dir = DATASET_DIR / dataset_name
        if not os.path.exists(dataset_dir):
            return jsonify({
                'status': 'error',
                'message': f"数据集 {dataset_name} 不存在"
            }), 404
        
        # 检查数据集结构
        train_dir = dataset_dir / 'train'
        val_dir = dataset_dir / 'val'
        
        if not os.path.exists(train_dir):
            return jsonify({
                'status': 'error',
                'message': f"数据集 {dataset_name} 缺少训练数据"
            }), 400
        
        # 准备训练数据
        train_data = {'images': [], 'labels': []}
        val_data = {'images': [], 'labels': []} if os.path.exists(val_dir) else None
        
        # 获取类别列表
        classes = [d.name for d in train_dir.iterdir() if d.is_dir()]
        class_to_idx = {cls: i for i, cls in enumerate(classes)}
        
        # 收集训练数据
        for cls in classes:
            class_dir = train_dir / cls
            class_idx = class_to_idx[cls]
            
            for img_path in class_dir.iterdir():
                if img_path.is_file() and img_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    train_data['images'].append(str(img_path))
                    train_data['labels'].append(class_idx)
        
        # 收集验证数据
        if val_data is not None:
            for cls in classes:
                class_dir = val_dir / cls
                if not class_dir.exists():
                    continue
                    
                class_idx = class_to_idx[cls]
                
                for img_path in class_dir.iterdir():
                    if img_path.is_file() and img_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                        val_data['images'].append(str(img_path))
                        val_data['labels'].append(class_idx)
        
        # 创建训练器
        trainer = ModelTrainer(model_name, num_classes=len(classes))
        
        # 开始训练
        logger.info(f"开始训练模型 {model_name}，数据集: {dataset_name}，轮数: {epochs}")
        history = trainer.train(train_data, val_data, epochs=epochs, batch_size=batch_size)
        
        # 保存训练结果
        result_path = TRAIN_RESULT_DIR / f"{model_name}_result.json"
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump({
                'model_name': model_name,
                'dataset_name': dataset_name,
                'classes': classes,
                'class_to_idx': class_to_idx,
                'epochs': epochs,
                'batch_size': batch_size,
                'history': {
                    'train_loss': [float(x) for x in history['train_loss']],
                    'train_acc': [float(x) for x in history['train_acc']],
                    'val_loss': [float(x) for x in history['val_loss']] if 'val_loss' in history else [],
                    'val_acc': [float(x) for x in history['val_acc']] if 'val_acc' in history else []
                },
                'timestamp': int(time.time())
            }, f, indent=2)
        
        return jsonify({
            'status': 'success',
            'message': f"模型 {model_name} 训练完成",
            'data': {
                'model_name': model_name,
                'dataset_name': dataset_name,
                'classes': classes,
                'epochs': epochs,
                'history': history
            }
        })
    except Exception as e:
        logger.error(f"训练失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"训练失败: {str(e)}"
        }), 500

@train_bp.route('/results/<model_name>', methods=['GET'])
def get_training_result(model_name):
    """
    获取训练结果
    
    Args:
        model_name (str): 模型名称
        
    Returns:
        JSON: 训练结果
    """
    try:
        # 检查结果文件是否存在
        result_path = TRAIN_RESULT_DIR / f"{model_name}_result.json"
        if not os.path.exists(result_path):
            return jsonify({
                'status': 'error',
                'message': f"模型 {model_name} 的训练结果不存在"
            }), 404
        
        # 读取训练结果
        with open(result_path, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        logger.error(f"获取训练结果失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取训练结果失败: {str(e)}"
        }), 500