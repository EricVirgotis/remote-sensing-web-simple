# -*- coding: utf-8 -*-
"""
CNN模型定义模块

包含LeNet-5、AlexNet、VGGNet-16、GoogLeNet和ResNet50模型的定义
"""

import os
import logging
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, applications, optimizers, losses, metrics
from tensorflow.keras.preprocessing.image import ImageDataGenerator

logger = logging.getLogger(__name__)

def create_lenet5(input_shape=(256, 256, 3), num_classes=45):
    """
    创建LeNet-5模型
    
    Args:
        input_shape (tuple): 输入图像形状 (高度, 宽度, 通道数)
        num_classes (int): 类别数量
        
    Returns:
        tf.keras.Model: LeNet-5模型
    """
    model = models.Sequential([
        # 第一个卷积层
        layers.Conv2D(6, kernel_size=(5, 5), strides=(1, 1), activation='relu', padding='same', input_shape=input_shape),
        layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2)),
        
        # 第二个卷积层
        layers.Conv2D(16, kernel_size=(5, 5), strides=(1, 1), activation='relu', padding='valid'),
        layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2)),
        
        # 全连接层
        layers.Flatten(),
        layers.Dense(120, activation='relu'),
        layers.Dense(84, activation='relu'),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

def create_alexnet(input_shape=(256, 256, 3), num_classes=45, use_pretrained=False):
    """
    创建AlexNet模型
    
    Args:
        input_shape (tuple): 输入图像形状 (高度, 宽度, 通道数)
        num_classes (int): 类别数量
        use_pretrained (bool): 是否使用预训练权重
        
    Returns:
        tf.keras.Model: AlexNet模型
    """
    # AlexNet没有在tf.keras.applications中，需要手动定义
    model = models.Sequential([
        # 第一个卷积层
        layers.Conv2D(96, kernel_size=(11, 11), strides=(4, 4), activation='relu', input_shape=input_shape, padding='same'),
        layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2)),
        layers.BatchNormalization(),
        
        # 第二个卷积层
        layers.Conv2D(256, kernel_size=(5, 5), strides=(1, 1), activation='relu', padding='same'),
        layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2)),
        layers.BatchNormalization(),
        
        # 第三个卷积层
        layers.Conv2D(384, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same'),
        
        # 第四个卷积层
        layers.Conv2D(384, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same'),
        
        # 第五个卷积层
        layers.Conv2D(256, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same'),
        layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2)),
        
        # 全连接层
        layers.Flatten(),
        layers.Dense(4096, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(4096, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

def create_vggnet16(input_shape=(256, 256, 3), num_classes=45, use_pretrained=False):
    """
    创建VGGNet-16模型
    
    Args:
        input_shape (tuple): 输入图像形状 (高度, 宽度, 通道数)
        num_classes (int): 类别数量
        use_pretrained (bool): 是否使用预训练权重
        
    Returns:
        tf.keras.Model: VGGNet-16模型
    """
    # 使用tf.keras.applications中的VGG16
    if use_pretrained:
        base_model = applications.VGG16(weights='imagenet', include_top=False, input_shape=input_shape)
    else:
        base_model = applications.VGG16(weights=None, include_top=False, input_shape=input_shape)
    
    # 添加分类头
    model = models.Sequential([
        base_model,
        layers.Flatten(),
        layers.Dense(4096, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(4096, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

def create_googlenet(input_shape=(256, 256, 3), num_classes=45, use_pretrained=False):
    """
    创建GoogLeNet (Inception v1) 模型
    
    Args:
        input_shape (tuple): 输入图像形状 (高度, 宽度, 通道数)
        num_classes (int): 类别数量
        use_pretrained (bool): 是否使用预训练权重
        
    Returns:
        tf.keras.Model: GoogLeNet模型
    """
    # 使用tf.keras.applications中的InceptionV3（注意：Keras没有提供InceptionV1，使用V3代替）
    if use_pretrained:
        base_model = applications.InceptionV3(weights='imagenet', include_top=False, input_shape=input_shape)
    else:
        base_model = applications.InceptionV3(weights=None, include_top=False, input_shape=input_shape)
    
    # 添加分类头
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(1024, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

def create_resnet50(input_shape=(256, 256, 3), num_classes=45, use_pretrained=False):
    """
    创建ResNet50模型
    
    Args:
        input_shape (tuple): 输入图像形状 (高度, 宽度, 通道数)
        num_classes (int): 类别数量
        use_pretrained (bool): 是否使用预训练权重
        
    Returns:
        tf.keras.Model: ResNet50模型
    """
    # 使用tf.keras.applications中的ResNet50
    if use_pretrained:
        base_model = applications.ResNet50(weights='imagenet', include_top=False, input_shape=input_shape)
    else:
        base_model = applications.ResNet50(weights=None, include_top=False, input_shape=input_shape)
    
    # 添加分类头
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(1024, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

def create_model(model_name, input_shape=(256, 256, 3), num_classes=45, use_pretrained=False):
    """
    根据模型名称创建相应的模型
    
    Args:
        model_name (str): 模型名称
        input_shape (tuple): 输入图像形状 (高度, 宽度, 通道数)
        num_classes (int): 类别数量
        use_pretrained (bool): 是否使用预训练权重
        
    Returns:
        tf.keras.Model: 创建的模型
    """
    if model_name == 'LeNet-5':
        return create_lenet5(input_shape, num_classes)
    elif model_name == 'AlexNet':
        return create_alexnet(input_shape, num_classes, use_pretrained)
    elif model_name == 'VGGNet-16':
        return create_vggnet16(input_shape, num_classes, use_pretrained)
    elif model_name == 'GoogleNet':
        return create_googlenet(input_shape, num_classes, use_pretrained)
    elif model_name == 'ResNet50':
        return create_resnet50(input_shape, num_classes, use_pretrained)
    else:
        raise ValueError(f"不支持的模型名称: {model_name}")