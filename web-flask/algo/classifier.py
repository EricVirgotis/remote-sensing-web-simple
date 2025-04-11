# -*- coding: utf-8 -*-
"""
分类算法模块

负责遥感影像的分类预测
"""

import os
import logging
import numpy as np
import torch
import time
from pathlib import Path
from .model_loader import load_model, get_default_model
from .preprocessing import ImagePreprocessor

logger = logging.getLogger(__name__)

# 类别映射
CLASS_MAPPING = {
    0: "农田",
    1: "森林",
    2: "草地",
    3: "水体",
    4: "城市建筑",
    5: "裸地",
    6: "其他"
}

class RemoteSensingClassifier:
    """
    遥感影像分类器
    """
    def __init__(self, model_name=None, device=None):
        """
        初始化分类器
        
        Args:
            model_name (str, optional): 模型名称，如果为None则使用默认模型
            device (str, optional): 设备类型 ('cuda' 或 'cpu')，如果为None则自动选择
        """
        # 设置设备
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        logger.info(f"使用设备: {self.device}")
        
        # 加载模型
        if model_name is None:
            model_name = get_default_model()
            if model_name is None:
                raise ValueError("没有可用的默认模型")
        
        self.model_name = model_name
        self.model = load_model(model_name)
        self.model.to(self.device)
        
        # 创建预处理器
        self.preprocessor = ImagePreprocessor()
    
    def predict(self, image_path):
        """
        对单个遥感影像进行分类预测
        
        Args:
            image_path (str): 影像文件路径
            
        Returns:
            dict: 预测结果，包含类别ID、类别名称和置信度
        """
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 读取并预处理图像
            image = self.preprocessor.read_image(image_path)
            tensor_image = self.preprocessor.preprocess(image)
            
            # 添加批次维度
            batch_image = tensor_image.unsqueeze(0).to(self.device)
            
            # 推理
            if isinstance(self.model, torch.nn.Module):
                with torch.no_grad():
                    outputs = self.model(batch_image)
                    probabilities = torch.softmax(outputs, dim=1)[0]
                    predicted_class = torch.argmax(probabilities).item()
                    confidence = probabilities[predicted_class].item()
            else:  # TensorFlow模型
                import tensorflow as tf
                # 转换为numpy数组
                image_array = batch_image.cpu().numpy()
                # TensorFlow模型预测
                predictions = self.model.predict(image_array)
                probabilities = tf.nn.softmax(predictions[0])
                predicted_class = tf.argmax(probabilities).numpy()
                confidence = float(probabilities[predicted_class])
            
            # 获取类别名称
            class_name = CLASS_MAPPING.get(predicted_class, f"未知类别_{predicted_class}")
            
            # 计算耗时
            elapsed_time = time.time() - start_time
            
            # 返回结果
            result = {
                'class_id': predicted_class,
                'class_name': class_name,
                'confidence': float(confidence),
                'processing_time': elapsed_time
            }
            
            logger.info(f"预测完成: {image_path} -> {class_name} (置信度: {confidence:.4f})")
            return result
            
        except Exception as e:
            logger.error(f"预测失败: {str(e)}")
            raise
    
    def predict_batch(self, image_paths):
        """
        批量预测多个遥感影像
        
        Args:
            image_paths (list): 影像文件路径列表
            
        Returns:
            list: 预测结果列表
        """
        try:
            results = []
            for image_path in image_paths:
                try:
                    result = self.predict(image_path)
                    results.append({
                        'image_path': image_path,
                        'prediction': result
                    })
                except Exception as e:
                    logger.error(f"处理图像 {image_path} 失败: {str(e)}")
                    results.append({
                        'image_path': image_path,
                        'error': str(e)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"批量预测失败: {str(e)}")
            raise
    
    def segment(self, image_path, tile_size=256, overlap=32):
        """
        对大型遥感影像进行分割分类
        
        将大图分割成小块，分别预测后合并结果
        
        Args:
            image_path (str): 影像文件路径
            tile_size (int): 分割块大小
            overlap (int): 重叠像素数
            
        Returns:
            dict: 分割分类结果
        """
        try:
            # 读取图像
            image = self.preprocessor.read_image(image_path)
            height, width = image.shape[:2]
            
            # 计算分割块数量
            stride = tile_size - overlap
            h_tiles = max(1, (height - overlap) // stride)
            w_tiles = max(1, (width - overlap) // stride)
            
            # 存储每个类别的像素数
            class_pixels = {class_id: 0 for class_id in CLASS_MAPPING.keys()}
            
            # 分割并预测
            for h in range(h_tiles):
                for w in range(w_tiles):
                    # 计算当前块的坐标
                    h_start = h * stride
                    w_start = w * stride
                    h_end = min(h_start + tile_size, height)
                    w_end = min(w_start + tile_size, width)
                    
                    # 提取图像块
                    tile = image[h_start:h_end, w_start:w_end]
                    
                    # 预处理并预测
                    tensor_tile = self.preprocessor.preprocess(tile)
                    batch_tile = tensor_tile.unsqueeze(0).to(self.device)
                    
                    if isinstance(self.model, torch.nn.Module):
                        with torch.no_grad():
                            outputs = self.model(batch_tile)
                            probabilities = torch.softmax(outputs, dim=1)[0]
                            predicted_class = torch.argmax(probabilities).item()
                    else:  # TensorFlow模型
                        import tensorflow as tf
                        # 转换为numpy数组
                        tile_array = batch_tile.cpu().numpy()
                        # TensorFlow模型预测
                        predictions = self.model.predict(tile_array)
                        probabilities = tf.nn.softmax(predictions[0])
                        predicted_class = tf.argmax(probabilities).numpy()
                    
                    # 累计像素数
                    tile_pixels = (h_end - h_start) * (w_end - w_start)
                    class_pixels[predicted_class] += tile_pixels
            
            # 计算每个类别的面积占比
            total_pixels = height * width
            class_percentages = {}
            for class_id, pixels in class_pixels.items():
                percentage = (pixels / total_pixels) * 100
                class_name = CLASS_MAPPING.get(class_id, f"未知类别_{class_id}")
                class_percentages[class_name] = percentage
            
            # 确定主要类别（占比最大的类别）
            main_class_id = max(class_pixels, key=class_pixels.get)
            main_class_name = CLASS_MAPPING.get(main_class_id, f"未知类别_{main_class_id}")
            main_class_percentage = (class_pixels[main_class_id] / total_pixels) * 100
            
            # 返回结果
            return {
                'main_class': {
                    'class_id': main_class_id,
                    'class_name': main_class_name,
                    'percentage': main_class_percentage
                },
                'class_distribution': class_percentages
            }
            
        except Exception as e:
            logger.error(f"分割分类失败: {str(e)}")
            raise