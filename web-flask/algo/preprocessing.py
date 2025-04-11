# -*- coding: utf-8 -*-
"""
数据预处理模块

负责遥感影像的读取、预处理和数据增强
"""

import os
import logging
import numpy as np
import cv2
from pathlib import Path
from osgeo import gdal
import torch
from torchvision import transforms

logger = logging.getLogger(__name__)

class ImagePreprocessor:
    """
    遥感影像预处理器
    """
    def __init__(self, image_size=(256, 256)):
        """
        初始化预处理器
        
        Args:
            image_size (tuple): 图像调整大小 (高度, 宽度)
        """
        self.image_size = image_size
        
        # 定义标准化变换
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def read_image(self, image_path):
        """
        读取遥感影像文件
        
        支持常见的遥感影像格式，如TIFF、IMG等
        
        Args:
            image_path (str): 影像文件路径
            
        Returns:
            numpy.ndarray: 读取的影像数据
        """
        try:
            file_ext = Path(image_path).suffix.lower()
            
            # 使用GDAL读取遥感影像
            if file_ext in ['.tif', '.tiff', '.img']:
                return self._read_with_gdal(image_path)
            
            # 使用OpenCV读取普通图像
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                return self._read_with_opencv(image_path)
            
            else:
                raise ValueError(f"不支持的文件格式: {file_ext}")
                
        except Exception as e:
            logger.error(f"读取影像文件失败: {str(e)}")
            raise
    
    def _read_with_gdal(self, image_path):
        """
        使用GDAL读取遥感影像
        
        Args:
            image_path (str): 影像文件路径
            
        Returns:
            numpy.ndarray: 读取的影像数据，形状为 (H, W, C)
        """
        try:
            # 打开数据集
            dataset = gdal.Open(image_path, gdal.GA_ReadOnly)
            if dataset is None:
                raise IOError(f"无法打开影像文件: {image_path}")
            
            # 获取波段数
            band_count = dataset.RasterCount
            if band_count < 1:
                raise ValueError(f"影像文件没有有效波段: {image_path}")
            
            # 读取数据
            width = dataset.RasterXSize
            height = dataset.RasterYSize
            
            # 创建输出数组
            image_data = np.zeros((height, width, min(band_count, 3)), dtype=np.uint8)
            
            # 读取前三个波段（RGB）
            for i in range(min(band_count, 3)):
                band = dataset.GetRasterBand(i + 1)
                image_data[:, :, i] = band.ReadAsArray()
            
            # 如果只有一个波段，复制到三个通道
            if band_count == 1:
                image_data = np.repeat(image_data[:, :, 0:1], 3, axis=2)
            
            return image_data
            
        except Exception as e:
            logger.error(f"GDAL读取影像失败: {str(e)}")
            raise
    
    def _read_with_opencv(self, image_path):
        """
        使用OpenCV读取普通图像
        
        Args:
            image_path (str): 图像文件路径
            
        Returns:
            numpy.ndarray: 读取的图像数据，形状为 (H, W, C)
        """
        try:
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                raise IOError(f"无法打开图像文件: {image_path}")
            
            # 转换为RGB格式
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 确保图像为3通道
            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 1:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
            
            # 归一化到0-1范围
            image = image.astype(np.float32) / 255.0
            
            return image
            
        except Exception as e:
            logger.error(f"OpenCV读取图像失败: {str(e)}")
            raise
    
    def preprocess(self, image):
        """
        预处理图像
        
        Args:
            image (numpy.ndarray): 输入图像，形状为 (H, W, C)
            
        Returns:
            torch.Tensor: 预处理后的图像张量，形状为 (C, H, W)
        """
        try:
            # 调整图像大小
            resized_image = cv2.resize(image, self.image_size)
            
            # 应用变换
            tensor_image = self.transform(resized_image)
            
            return tensor_image
            
        except Exception as e:
            logger.error(f"图像预处理失败: {str(e)}")
            raise
    
    def batch_preprocess(self, images):
        """
        批量预处理图像
        
        Args:
            images (list): 输入图像列表
            
        Returns:
            torch.Tensor: 预处理后的图像张量批次，形状为 (B, C, H, W)
        """
        try:
            processed_images = [self.preprocess(img) for img in images]
            return torch.stack(processed_images)
            
        except Exception as e:
            logger.error(f"批量图像预处理失败: {str(e)}")
            raise

# 数据增强函数
def get_train_transforms(image_size=(256, 256)):
    """
    获取训练数据增强变换
    
    Args:
        image_size (tuple): 图像大小 (高度, 宽度)
        
    Returns:
        torchvision.transforms: 数据增强变换
    """
    return transforms.Compose([
        transforms.ToPILImage(),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
        transforms.Resize(image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

def get_val_transforms(image_size=(256, 256)):
    """
    获取验证数据变换
    
    Args:
        image_size (tuple): 图像大小 (高度, 宽度)
        
    Returns:
        torchvision.transforms: 数据变换
    """
    return transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize(image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])