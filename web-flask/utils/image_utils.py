# -*- coding: utf-8 -*-
"""
图像处理工具模块

提供图像处理相关的辅助功能
"""

import os
import logging
import numpy as np
import cv2
from pathlib import Path
from osgeo import gdal
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

logger = logging.getLogger(__name__)

# 类别颜色映射
CLASS_COLORS = {
    0: [255, 255, 0],    # 农田 - 黄色
    1: [0, 128, 0],      # 森林 - 绿色
    2: [144, 238, 144],  # 草地 - 浅绿色
    3: [0, 0, 255],      # 水体 - 蓝色
    4: [128, 128, 128],  # 城市建筑 - 灰色
    5: [210, 180, 140],  # 裸地 - 棕色
    6: [255, 0, 255]     # 其他 - 紫色
}

def read_image(image_path):
    """
    读取图像文件
    
    支持常见的图像格式和遥感影像格式
    
    Args:
        image_path (str or Path): 图像文件路径
        
    Returns:
        numpy.ndarray: 读取的图像数据，形状为 (H, W, C)
    """
    try:
        image_path = Path(image_path)
        file_ext = image_path.suffix.lower()
        
        # 使用GDAL读取遥感影像
        if file_ext in ['.tif', '.tiff', '.img']:
            return read_with_gdal(image_path)
        
        # 使用OpenCV读取普通图像
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            return read_with_opencv(image_path)
        
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")
            
    except Exception as e:
        logger.error(f"读取图像文件失败: {str(e)}")
        raise

def read_with_gdal(image_path):
    """
    使用GDAL读取遥感影像
    
    Args:
        image_path (str or Path): 影像文件路径
        
    Returns:
        numpy.ndarray: 读取的影像数据，形状为 (H, W, C)
    """
    try:
        # 打开数据集
        dataset = gdal.Open(str(image_path), gdal.GA_ReadOnly)
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

def read_with_opencv(image_path):
    """
    使用OpenCV读取普通图像
    
    Args:
        image_path (str or Path): 图像文件路径
        
    Returns:
        numpy.ndarray: 读取的图像数据，形状为 (H, W, C)
    """
    try:
        # 读取图像
        image = cv2.imread(str(image_path))
        if image is None:
            raise IOError(f"无法打开图像文件: {image_path}")
        
        # 转换为RGB格式
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        return image
        
    except Exception as e:
        logger.error(f"OpenCV读取图像失败: {str(e)}")
        raise

def save_image(image, save_path, format=None):
    """
    保存图像
    
    Args:
        image (numpy.ndarray): 图像数据，形状为 (H, W, C)
        save_path (str or Path): 保存路径
        format (str, optional): 图像格式，如果为None则根据文件扩展名确定
        
    Returns:
        bool: 是否成功保存
    """
    try:
        save_path = Path(save_path)
        
        # 确保目录存在
        os.makedirs(save_path.parent, exist_ok=True)
        
        # 确定图像格式
        if format is None:
            format = save_path.suffix.lower().lstrip('.')
            if not format:
                format = 'png'
                save_path = save_path.with_suffix('.png')
        
        # 转换为BGR格式（OpenCV使用BGR）
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image
        
        # 保存图像
        cv2.imwrite(str(save_path), image_bgr)
        
        return True
        
    except Exception as e:
        logger.error(f"保存图像失败: {str(e)}")
        return False

def resize_image(image, size):
    """
    调整图像大小
    
    Args:
        image (numpy.ndarray): 图像数据，形状为 (H, W, C)
        size (tuple): 目标大小 (宽度, 高度)
        
    Returns:
        numpy.ndarray: 调整大小后的图像
    """
    try:
        return cv2.resize(image, size)
    except Exception as e:
        logger.error(f"调整图像大小失败: {str(e)}")
        raise

def create_classification_visualization(image, class_id, save_path=None):
    """
    创建分类结果可视化图像
    
    Args:
        image (numpy.ndarray): 原始图像
        class_id (int): 类别ID
        save_path (str or Path, optional): 保存路径，如果为None则不保存
        
    Returns:
        numpy.ndarray: 可视化图像
    """
    try:
        # 获取类别颜色
        color = CLASS_COLORS.get(class_id, [255, 255, 255])  # 默认白色
        
        # 创建边框
        h, w = image.shape[:2]
        border_width = max(5, int(min(h, w) * 0.02))  # 边框宽度，至少5像素
        
        # 复制图像
        vis_image = image.copy()
        
        # 添加边框
        vis_image[:border_width, :] = color  # 上边框
        vis_image[-border_width:, :] = color  # 下边框
        vis_image[:, :border_width] = color  # 左边框
        vis_image[:, -border_width:] = color  # 右边框
        
        # 保存图像
        if save_path is not None:
            save_image(vis_image, save_path)
        
        return vis_image
        
    except Exception as e:
        logger.error(f"创建分类可视化失败: {str(e)}")
        raise

def create_segmentation_visualization(image, class_map, save_path=None, alpha=0.5):
    """
    创建分割结果可视化图像
    
    Args:
        image (numpy.ndarray): 原始图像
        class_map (numpy.ndarray): 类别图，形状为 (H, W)，值为类别ID
        save_path (str or Path, optional): 保存路径，如果为None则不保存
        alpha (float): 透明度，范围 [0, 1]
        
    Returns:
        numpy.ndarray: 可视化图像
    """
    try:
        # 创建彩色类别图
        h, w = class_map.shape
        color_map = np.zeros((h, w, 3), dtype=np.uint8)
        
        # 为每个类别填充颜色
        for class_id, color in CLASS_COLORS.items():
            mask = (class_map == class_id)
            color_map[mask] = color
        
        # 调整原始图像大小以匹配类别图
        if image.shape[:2] != (h, w):
            image = resize_image(image, (w, h))
        
        # 混合图像
        vis_image = cv2.addWeighted(image, 1 - alpha, color_map, alpha, 0)
        
        # 保存图像
        if save_path is not None:
            save_image(vis_image, save_path)
        
        return vis_image
        
    except Exception as e:
        logger.error(f"创建分割可视化失败: {str(e)}")
        raise

def create_class_distribution_chart(class_distribution, save_path=None):
    """
    创建类别分布图表
    
    Args:
        class_distribution (dict): 类别分布，键为类别名称，值为百分比
        save_path (str or Path, optional): 保存路径，如果为None则不保存
        
    Returns:
        matplotlib.figure.Figure: 图表对象
    """
    try:
        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 准备数据
        classes = list(class_distribution.keys())
        percentages = list(class_distribution.values())
        
        # 创建柱状图
        bars = ax.bar(classes, percentages, color='skyblue')
        
        # 添加数据标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        # 设置标题和标签
        ax.set_title('类别分布', fontsize=16)
        ax.set_xlabel('类别', fontsize=12)
        ax.set_ylabel('百分比 (%)', fontsize=12)
        
        # 设置Y轴范围
        ax.set_ylim(0, max(percentages) * 1.2)
        
        # 旋转X轴标签
        plt.xticks(rotation=45, ha='right')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        if save_path is not None:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
        
    except Exception as e:
        logger.error(f"创建类别分布图表失败: {str(e)}")
        raise