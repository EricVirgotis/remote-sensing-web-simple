# -*- coding: utf-8 -*-
"""
模型训练模块

负责遥感影像分类模型的训练
"""

import os
import logging
import time
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from .preprocessing import get_train_transforms, get_val_transforms

logger = logging.getLogger(__name__)

# 模型存储路径
MODEL_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / '../models'

class RemoteSensingDataset(Dataset):
    """
    遥感影像数据集
    """
    def __init__(self, image_paths, labels, transform=None):
        """
        初始化数据集
        
        Args:
            image_paths (list): 图像路径列表
            labels (list): 标签列表
            transform (callable, optional): 数据变换
        """
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        # 读取图像
        image_path = self.image_paths[idx]
        try:
            import cv2
            image = cv2.imread(image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 应用变换
            if self.transform:
                image = self.transform(image)
            
            return image, self.labels[idx]
        except Exception as e:
            logger.error(f"读取图像失败 {image_path}: {str(e)}")
            # 返回一个空图像和标签
            if self.transform:
                dummy_image = torch.zeros(3, 256, 256)
            else:
                dummy_image = np.zeros((256, 256, 3), dtype=np.uint8)
            return dummy_image, self.labels[idx]

class ModelTrainer:
    """
    遥感影像分类模型训练器
    """
    def __init__(self, model_name, num_classes=7, device=None):
        """
        初始化训练器
        
        Args:
            model_name (str): 模型名称
            num_classes (int): 类别数量
            device (str, optional): 设备类型 ('cuda' 或 'cpu')，如果为None则自动选择
        """
        # 设置设备
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        logger.info(f"使用设备: {self.device}")
        
        # 创建模型
        self.model_name = model_name
        self.num_classes = num_classes
        self.model = self._create_model()
        self.model.to(self.device)
        
        # 创建损失函数和优化器
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, mode='min', factor=0.5, patience=5)
        
        # 确保模型目录存在
        os.makedirs(MODEL_DIR, exist_ok=True)
    
    def _create_model(self):
        """
        创建模型
        
        Returns:
            torch.nn.Module: 创建的模型
        """
        try:
            # 使用预训练的ResNet50模型
            import torchvision.models as models
            model = models.resnet50(pretrained=True)
            
            # 修改最后一层以适应类别数量
            in_features = model.fc.in_features
            model.fc = nn.Linear(in_features, self.num_classes)
            
            return model
        except Exception as e:
            logger.error(f"创建模型失败: {str(e)}")
            raise
    
    def train(self, train_data, val_data=None, epochs=30, batch_size=32, save_interval=5):
        """
        训练模型
        
        Args:
            train_data (dict): 训练数据，包含 'images' 和 'labels' 键
            val_data (dict, optional): 验证数据，包含 'images' 和 'labels' 键
            epochs (int): 训练轮数
            batch_size (int): 批次大小
            save_interval (int): 保存模型的间隔轮数
            
        Returns:
            dict: 训练历史记录
        """
        try:
            # 准备数据集
            train_transform = get_train_transforms()
            val_transform = get_val_transforms()
            
            train_dataset = RemoteSensingDataset(
                train_data['images'],
                train_data['labels'],
                transform=train_transform
            )
            train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
            
            if val_data:
                val_dataset = RemoteSensingDataset(
                    val_data['images'],
                    val_data['labels'],
                    transform=val_transform
                )
                val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
            else:
                val_loader = None
            
            # 训练历史记录
            history = {
                'train_loss': [],
                'train_acc': [],
                'val_loss': [],
                'val_acc': []
            }
            
            # 训练循环
            best_val_acc = 0.0
            start_time = time.time()
            
            for epoch in range(epochs):
                # 训练阶段
                self.model.train()
                train_loss = 0.0
                train_correct = 0
                train_total = 0
                
                for images, labels in train_loader:
                    images, labels = images.to(self.device), labels.to(self.device)
                    
                    # 前向传播
                    self.optimizer.zero_grad()
                    outputs = self.model(images)
                    loss = self.criterion(outputs, labels)
                    
                    # 反向传播
                    loss.backward()
                    self.optimizer.step()
                    
                    # 统计
                    train_loss += loss.item() * images.size(0)
                    _, predicted = torch.max(outputs, 1)
                    train_total += labels.size(0)
                    train_correct += (predicted == labels).sum().item()
                
                # 计算训练指标
                epoch_train_loss = train_loss / train_total
                epoch_train_acc = train_correct / train_total
                history['train_loss'].append(epoch_train_loss)
                history['train_acc'].append(epoch_train_acc)
                
                # 验证阶段
                if val_loader:
                    self.model.eval()
                    val_loss = 0.0
                    val_correct = 0
                    val_total = 0
                    
                    with torch.no_grad():
                        for images, labels in val_loader:
                            images, labels = images.to(self.device), labels.to(self.device)
                            
                            # 前向传播
                            outputs = self.model(images)
                            loss = self.criterion(outputs, labels)
                            
                            # 统计
                            val_loss += loss.item() * images.size(0)
                            _, predicted = torch.max(outputs, 1)
                            val_total += labels.size(0)
                            val_correct += (predicted == labels).sum().item()
                    
                    # 计算验证指标
                    epoch_val_loss = val_loss / val_total
                    epoch_val_acc = val_correct / val_total
                    history['val_loss'].append(epoch_val_loss)
                    history['val_acc'].append(epoch_val_acc)
                    
                    # 更新学习率
                    self.scheduler.step(epoch_val_loss)
                    
                    # 保存最佳模型
                    if epoch_val_acc > best_val_acc:
                        best_val_acc = epoch_val_acc
                        self.save_model(f"{self.model_name}_best")
                        logger.info(f"保存最佳模型，验证准确率: {epoch_val_acc:.4f}")
                
                # 打印进度
                if val_loader:
                    logger.info(f"Epoch {epoch+1}/{epochs} - "
                              f"Train Loss: {epoch_train_loss:.4f}, "
                              f"Train Acc: {epoch_train_acc:.4f}, "
                              f"Val Loss: {epoch_val_loss:.4f}, "
                              f"Val Acc: {epoch_val_acc:.4f}")
                else:
                    logger.info(f"Epoch {epoch+1}/{epochs} - "
                              f"Train Loss: {epoch_train_loss:.4f}, "
                              f"Train Acc: {epoch_train_acc:.4f}")
                
                # 定期保存模型
                if (epoch + 1) % save_interval == 0:
                    self.save_model(f"{self.model_name}_epoch{epoch+1}")
            
            # 保存最终模型
            self.save_model(self.model_name)
            
            # 计算总训练时间
            total_time = time.time() - start_time
            logger.info(f"训练完成，总耗时: {total_time:.2f}秒")
            
            return history
            
        except Exception as e:
            logger.error(f"训练失败: {str(e)}")
            raise
    
    def save_model(self, model_name=None):
        """
        保存模型
        
        Args:
            model_name (str, optional): 模型名称，如果为None则使用初始化时的名称
        """
        if model_name is None:
            model_name = self.model_name
        
        model_path = MODEL_DIR / f"{model_name}.pt"
        torch.save(self.model, model_path)
        logger.info(f"模型已保存: {model_path}")
    
    def evaluate(self, test_data, batch_size=32):
        """
        评估模型
        
        Args:
            test_data (dict): 测试数据，包含 'images' 和 'labels' 键
            batch_size (int): 批次大小
            
        Returns:
            dict: 评估结果
        """
        try:
            # 准备数据集
            test_transform = get_val_transforms()
            test_dataset = RemoteSensingDataset(
                test_data['images'],
                test_data['labels'],
                transform=test_transform
            )
            test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
            
            # 评估
            self.model.eval()
            test_loss = 0.0
            test_correct = 0
            test_total = 0
            
            # 混淆矩阵
            confusion_matrix = np.zeros((self.num_classes, self.num_classes), dtype=np.int64)
            
            with torch.no_grad():
                for images, labels in test_loader:
                    images, labels = images.to(self.device), labels.to(self.device)
                    
                    # 前向传播
                    outputs = self.model(images)
                    loss = self.criterion(outputs, labels)
                    
                    # 统计
                    test_loss += loss.item() * images.size(0)
                    _, predicted = torch.max(outputs, 1)
                    test_total += labels.size(0)
                    test_correct += (predicted == labels).sum().item()
                    
                    # 更新混淆矩阵
                    for i in range(len(labels)):
                        confusion_matrix[labels[i].item()][predicted[i].item()] += 1
            
            # 计算指标
            test_loss = test_loss / test_total
            test_acc = test_correct / test_total
            
            # 计算每个类别的精确率和召回率
            precision = np.zeros(self.num_classes)
            recall = np.zeros(self.num_classes)
            f1_score = np.zeros(self.num_classes)
            
            for i in range(self.num_classes):
                # 精确率 = TP / (TP + FP)
                if np.sum(confusion_matrix[:, i]) > 0:
                    precision[i] = confusion_matrix[i, i] / np.sum(confusion_matrix[:, i])
                
                # 召回率 = TP / (TP + FN)
                if np.sum(confusion_matrix[i, :]) > 0:
                    recall[i] = confusion_matrix[i, i] / np.sum(confusion_matrix[i, :])
                
                # F1分数 = 2 * (精确率 * 召回率) / (精确率 + 召回率)
                if precision[i] + recall[i] > 0:
                    f1_score[i] = 2 * precision[i] * recall[i] / (precision[i] + recall[i])
            
            # 计算宏平均和微平均
            macro_precision = np.mean(precision)
            macro_recall = np.mean(recall)
            macro_f1 = np.mean(f1_score)
            
            micro_precision = test_correct / test_total
            micro_recall = test_correct / test_total
            micro_f1 = test_correct / test_total
            
            # 返回结果
            return {
                'test_loss': test_loss,
                'test_acc': test_acc,
                'confusion_matrix': confusion_matrix.tolist(),
                'class_metrics': {
                    'precision': precision.tolist(),
                    'recall': recall.tolist(),
                    'f1_score': f1_score.tolist()
                },
                'macro_metrics': {
                    'precision': macro_precision,
                    'recall': macro_recall,
                    'f1': macro_f1
                },
                'micro_metrics': {
                    'precision': micro_precision,
                    'recall': micro_recall,
                    'f1': micro_f1
                }
            }
            
        except Exception as e:
            logger.error(f"评估失败: {str(e)}")
            raise