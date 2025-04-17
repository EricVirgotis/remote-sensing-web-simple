# -*- coding: utf-8 -*-
"""
CNN模型定义模块

包含LeNet-5、AlexNet、VGGNet-16、GoogLeNet和ResNet50模型的定义
"""

import os
import logging
import torch
import torch.nn as nn
import torchvision.models as models

logger = logging.getLogger(__name__)

class LeNet5(nn.Module):
    def __init__(self, num_classes=45):
        super(LeNet5, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 6, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(6, 16, kernel_size=5),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        self.classifier = nn.Sequential(
            nn.Linear(16 * 61 * 61, 120),
            nn.ReLU(),
            nn.Linear(120, 84),
            nn.ReLU(),
            nn.Linear(84, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x

def create_lenet5(num_classes=45):
    """
    创建LeNet-5模型
    
    Args:
        num_classes (int): 类别数量
        
    Returns:
        torch.nn.Module: LeNet-5模型
    """
    return LeNet5(num_classes=num_classes)

def create_alexnet(num_classes=45, use_pretrained=False):
    """
    创建AlexNet模型
    
    Args:
        num_classes (int): 类别数量
        use_pretrained (bool): 是否使用预训练权重
        
    Returns:
        torch.nn.Module: AlexNet模型
    """
    model = models.alexnet(weights='DEFAULT' if use_pretrained else None)
    model.classifier[6] = nn.Linear(4096, num_classes)
    return model

def create_vggnet16(num_classes=45, use_pretrained=False):
    """
    创建VGGNet-16模型
    
    Args:
        num_classes (int): 类别数量
        use_pretrained (bool): 是否使用预训练权重
        
    Returns:
        torch.nn.Module: VGGNet-16模型
    """
    model = models.vgg16(weights='DEFAULT' if use_pretrained else None)
    model.classifier[6] = nn.Linear(4096, num_classes)
    return model

def create_googlenet(num_classes=45, use_pretrained=False):
    """
    创建GoogLeNet模型
    
    Args:
        num_classes (int): 类别数量
        use_pretrained (bool): 是否使用预训练权重
        
    Returns:
        torch.nn.Module: GoogLeNet模型
    """
    model = models.googlenet(weights='DEFAULT' if use_pretrained else None)
    model.fc = nn.Linear(1024, num_classes)
    return model

def create_resnet50(num_classes=45, use_pretrained=False):
    """
    创建ResNet50模型
    
    Args:
        num_classes (int): 类别数量
        use_pretrained (bool): 是否使用预训练权重
        
    Returns:
        torch.nn.Module: ResNet50模型
    """
    model = models.resnet50(weights='DEFAULT' if use_pretrained else None)
    model.fc = nn.Linear(2048, num_classes)
    return model

def create_model(model_name, num_classes=45, use_pretrained=False):
    """
    根据模型名称创建相应的模型
    
    Args:
        model_name (str): 模型名称
        num_classes (int): 类别数量
        use_pretrained (bool): 是否使用预训练权重
        
    Returns:
        torch.nn.Module: 创建的模型
    """
    try:
        if model_name == 'LeNet-5':
            return create_lenet5(num_classes)
        elif model_name == 'AlexNet':
            return create_alexnet(num_classes, use_pretrained)
        elif model_name == 'VGGNet-16':
            return create_vggnet16(num_classes, use_pretrained)
        elif model_name == 'GoogleNet':
            return create_googlenet(num_classes, use_pretrained)
        elif model_name == 'ResNet50':
            return create_resnet50(num_classes, use_pretrained)
        else:
            raise ValueError(f"不支持的模型名称: {model_name}")
    except Exception as e:
        logger.error(f"创建模型失败: {str(e)}")
        raise