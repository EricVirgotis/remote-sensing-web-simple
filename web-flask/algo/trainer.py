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
import albumentations as A
from tqdm import tqdm
from .preprocessing import get_train_transforms, get_val_transforms

# 设置环境变量以屏蔽albumentations更新提示
os.environ['NO_ALBUMENTATIONS_UPDATE'] = '1'

logger = logging.getLogger(__name__)

# 模型存储路径
MODEL_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) / 'file_store/model'

class RemoteSensingDataset(Dataset):
    """
    遥感影像数据集
    """
    def __init__(self, data_dir=None, image_paths=None, labels=None, transform=None):
        """
        初始化数据集
        
        Args:
            data_dir (str, optional): 数据集根目录，如果提供则自动从目录结构构建数据集
            image_paths (list, optional): 图像路径列表
            labels (list, optional): 标签列表
            transform (callable, optional): 数据变换
        """
        self.transform = transform
        self.label_to_idx = {}
        self.idx_to_label = {}
        
        if data_dir is not None:
            # 从目录结构构建数据集
            self.image_paths = []
            self.labels = []
            self.class_names = []
            
            # 获取所有类别（子文件夹）
            class_dirs = [d for d in Path(data_dir).iterdir() if d.is_dir()]
            
            # 为每个类别分配数字标签
            for label_idx, class_dir in enumerate(sorted(class_dirs)):
                class_name = class_dir.name
                self.class_names.append(class_name)
                self.label_to_idx[class_name] = label_idx
                self.idx_to_label[label_idx] = class_name
                
                # 获取该类别下的所有图像
                image_files = [str(f) for f in class_dir.glob('*') 
                              if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']]
                
                self.image_paths.extend(image_files)
                self.labels.extend([label_idx] * len(image_files))
                
            logger.info(f"从目录 {data_dir} 加载数据集")
            logger.info(f"找到 {len(self.class_names)} 个类别: {self.class_names}")
            logger.info(f"总共 {len(self.image_paths)} 张图像")
        else:
            # 使用提供的图像路径和标签
            if image_paths is None or labels is None:
                raise ValueError("必须提供 data_dir 或同时提供 image_paths 和 labels")
            self.image_paths = image_paths
            
            # 处理标签
            unique_labels = sorted(set(labels))
            self.class_names = unique_labels
            self.label_to_idx = {label: idx for idx, label in enumerate(unique_labels)}
            self.idx_to_label = {idx: label for idx, label in enumerate(unique_labels)}
            
            # 将字符串标签转换为数值索引
            self.labels = [self.label_to_idx[label] if isinstance(label, str) else label for label in labels]
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        # 读取图像
        image_path = self.image_paths[idx]
        try:
            import cv2
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法读取图像文件: {image_path}")
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 应用变换
            if self.transform:
                if isinstance(self.transform, A.Compose):
                    # 对于albumentations变换
                    transformed = self.transform(image=image)
                    image = transformed["image"]
                else:
                    # 对于torchvision变换
                    image = self.transform(image)
            
            # 确保标签是tensor
            label = torch.tensor(self.labels[idx], dtype=torch.long)
            
            return image, label
        except Exception as e:
            logger.error(f"读取图像失败 {image_path}: {str(e)}")
            # 返回一个空图像和标签
            if self.transform:
                dummy_image = torch.zeros((3, 256, 256), dtype=torch.float32)
            else:
                dummy_image = np.zeros((256, 256, 3), dtype=np.uint8)
            return dummy_image, torch.tensor(self.labels[idx], dtype=torch.long)

class ModelTrainer:
    """
    遥感影像分类模型训练器
    """
    def __init__(self, model_name, num_classes=7, use_pretrained=True, device=None): # 添加 use_pretrained 参数
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
        self.use_pretrained = use_pretrained # 保存 use_pretrained
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
            import torchvision.models as models
            import torch.hub as hub
            
            if self.model_name == 'LeNet-5':
                model = nn.Sequential(
                    nn.Conv2d(3, 6, kernel_size=5),
                    nn.ReLU(),
                    nn.MaxPool2d(kernel_size=2, stride=2),
                    nn.Conv2d(6, 16, kernel_size=5),
                    nn.ReLU(),
                    nn.MaxPool2d(kernel_size=2, stride=2),
                    nn.Flatten(),
                    nn.Linear(16*53*53, 120),
                    nn.ReLU(),
                    nn.Linear(120, 84),
                    nn.ReLU(),
                    nn.Linear(84, self.num_classes)
                )
            elif self.model_name == 'AlexNet':
                # AlexNet 没有官方预训练权重
                if self.use_pretrained:
                    logger.warning("AlexNet不支持官方预训练权重，将使用随机初始化权重")
                model = models.alexnet(weights=None)
                model.classifier[6] = nn.Linear(model.classifier[6].in_features, self.num_classes)
            elif self.model_name == 'VGGNet-16':
                model = models.vgg16(weights=None)
                if self.use_pretrained:
                    try:
                        logger.info("正在下载VGG16预训练权重...")
                        state_dict = hub.load_state_dict_from_url(models.VGG16_Weights.IMAGENET1K_V1.url, progress=True)
                        model.load_state_dict(state_dict)
                        logger.info("成功加载VGG16预训练权重")
                    except Exception as e:
                        logger.error(f"加载VGG16预训练权重失败: {str(e)}")
                        raise ValueError("下载预训练权重失败，请检查网络连接或稍后重试")
                else:
                    logger.info("使用随机初始化权重")
                model.classifier[6] = nn.Linear(model.classifier[6].in_features, self.num_classes)
            elif self.model_name == 'GoogleNet':
                model = models.googlenet(weights=None)
                if self.use_pretrained:
                    try:
                        logger.info("正在下载GoogleNet预训练权重...")
                        state_dict = hub.load_state_dict_from_url(models.GoogLeNet_Weights.IMAGENET1K_V1.url, progress=True)
                        model.load_state_dict(state_dict)
                        logger.info("成功加载GoogleNet预训练权重")
                    except Exception as e:
                        logger.error(f"加载GoogleNet预训练权重失败: {str(e)}")
                        raise ValueError("下载预训练权重失败，请检查网络连接或稍后重试")
                else:
                    logger.info("使用随机初始化权重")
                model.fc = nn.Linear(model.fc.in_features, self.num_classes)
            elif self.model_name == 'ResNet50':
                model = models.resnet50(weights=None)
                if self.use_pretrained:
                    try:
                        logger.info("正在下载ResNet50预训练权重...")
                        state_dict = hub.load_state_dict_from_url(models.ResNet50_Weights.IMAGENET1K_V2.url, progress=True)
                        model.load_state_dict(state_dict)
                        logger.info("成功加载ResNet50预训练权重")
                    except Exception as e:
                        logger.error(f"加载ResNet50预训练权重失败: {str(e)}")
                        raise ValueError("下载预训练权重失败，请检查网络连接或稍后重试")
                else:
                    logger.info("使用随机初始化权重")
                model.fc = nn.Linear(model.fc.in_features, self.num_classes)
            else:
                raise ValueError(f"不支持的模型名称: {self.model_name}")
            
            return model
        except Exception as e:
            logger.error(f"创建模型失败: {str(e)}")
            raise    
    def train(self, train_data, val_data=None, epochs=30, batch_size=32, save_interval=5, task_id=None, user_id=None):
        """
        训练模型
        
        Args:
            train_data (dict): 训练数据，包含 'images' 和 'labels' 键
            val_data (dict, optional): 验证数据，包含 'images' 和 'labels' 键
            epochs (int): 训练轮数
            batch_size (int): 批次大小
            save_interval (int): 保存模型的间隔轮数
            task_id (int, optional): 训练任务ID，用于保存模型和清理临时文件
            user_id (int, optional): 用户ID，用于指定保存路径
            
        Returns:
            dict: 训练历史记录
        """
        try:
            # 准备数据集
            train_transform = get_train_transforms()
            val_transform = get_val_transforms()
            
            # 支持两种数据加载方式
            if isinstance(train_data, str):
                # 从目录加载数据集
                self.train_dataset = RemoteSensingDataset(
                    data_dir=train_data,
                    transform=train_transform
                )
                # 更新类别数量
                self.num_classes = len(self.train_dataset.class_names)
            else:
                # 使用传统方式加载数据集
                self.train_dataset = RemoteSensingDataset(
                    image_paths=train_data['images'],
                    labels=train_data['labels'],
                    transform=train_transform
                )
            
            train_loader = DataLoader(self.train_dataset, batch_size=batch_size, shuffle=True, num_workers=0) # 将num_workers设置为0以在Windows上兼容。
            
            if val_data:
                if isinstance(val_data, str):
                    val_dataset = RemoteSensingDataset(
                        data_dir=val_data,
                        transform=val_transform
                    )
                else:
                    val_dataset = RemoteSensingDataset(
                        image_paths=val_data['images'],
                        labels=val_data['labels'],
                        transform=val_transform
                    )
                val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0) # Set num_workers=0 for Windows compatibility
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
            # 更新训练开始时间
            from datetime import datetime
            from utils.db_utils import update_task_status
            from app import socketio # 导入 socketio 实例
            
            # 连接Redis
            # redis_client = redis.Redis(host='localhost', port=6379, db=0)
            
            # 更新任务状态并发布消息
            update_task_status(task_id, 1, start_time=datetime.now())
            status_message = {
                'taskId': task_id,
                'status': 1,
                'startTime': datetime.now().isoformat(),
                'message': '训练开始'
            }
            socketio.emit('training_status_update', status_message) # 使用 socketio 发送消息
            
            for epoch in range(epochs):
                # 训练阶段
                self.model.train()
                train_loss = 0.0
                train_correct = 0
                train_total = 0
                
                # 添加进度条
                train_pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{epochs} [Train]')
                for images, labels in train_pbar:
                    images, labels = images.to(self.device), labels.to(self.device)
                    
                    # 前向传播
                    self.optimizer.zero_grad()
                    outputs = self.model(images)
                    
                    # 处理GoogleNet特殊输出结构
                    if self.model_name == 'GoogleNet' and hasattr(outputs, 'logits'):
                        # GoogleNet返回的是GoogLeNetOutputs对象，需要提取logits
                        loss = self.criterion(outputs.logits, labels)
                        _, predicted = torch.max(outputs.logits, 1) # 使用 outputs.logits
                    else:
                        # 其他模型返回的是普通张量
                        loss = self.criterion(outputs, labels)
                        _, predicted = torch.max(outputs, 1)
                    
                    # 反向传播
                    loss.backward()
                    self.optimizer.step()
                    
                    # 统计
                    train_loss += loss.item() * images.size(0)
                    # _, predicted = torch.max(outputs, 1) # 这行已被移到上面条件判断中
                    train_total += labels.size(0)
                    train_correct += (predicted == labels).sum().item()
                    
                    # 更新进度条
                    current_loss = loss.item()
                    current_acc = (predicted == labels).sum().item() / labels.size(0)
                    train_pbar.set_postfix({'loss': f'{current_loss:.4f}', 'acc': f'{current_acc:.4f}'})
                
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
                        # 添加验证进度条
                        val_pbar = tqdm(val_loader, desc=f'Epoch {epoch+1}/{epochs} [Val]')
                        for images, labels in val_pbar:
                            images, labels = images.to(self.device), labels.to(self.device)
                            
                            # 前向传播
                            outputs = self.model(images)
                            
                            # 处理GoogleNet特殊输出结构
                            if self.model_name == 'GoogleNet' and hasattr(outputs, 'logits'):
                                # GoogleNet返回的是GoogLeNetOutputs对象，需要提取logits
                                loss = self.criterion(outputs.logits, labels)
                                _, predicted = torch.max(outputs.logits, 1)
                            else:
                                # 其他模型返回的是普通张量
                                loss = self.criterion(outputs, labels)
                                _, predicted = torch.max(outputs, 1)
                            
                            # 统计
                            val_loss += loss.item() * images.size(0)
                            # _, predicted = torch.max(outputs, 1) # 这行需要删除或注释掉，因为上面已经计算了 predicted
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
                        self.save_model(f"{self.model_name}_best", user_id=user_id, task_id=task_id)
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
                
                # 通过WebSocket发送进度更新
                progress_message = {
                    'taskId': task_id,
                    'status': 1, # 训练中
                    'epoch': epoch + 1,
                    'totalEpochs': epochs,
                    'trainLoss': epoch_train_loss,
                    'trainAcc': epoch_train_acc,
                    'valLoss': epoch_val_loss if val_loader else None,
                    'valAcc': epoch_val_acc if val_loader else None,
                    'message': f'Epoch {epoch+1} 完成'
                }
                socketio.emit('training_status_update', progress_message)

                # 定期保存模型
                if (epoch + 1) % save_interval == 0:
                    self.save_model(f"{self.model_name}_epoch{epoch+1}", user_id=user_id, task_id=task_id)
            
            # 保存最终模型
            self.save_model(f"{self.model_name}_final", user_id=user_id, task_id=task_id)
            
            # 训练成功，发送最终状态
            end_time = datetime.now()
            success_message = {
                'taskId': task_id,
                'status': 2, # 成功状态
                'endTime': end_time.isoformat(),
                'message': '训练成功完成',
                'finalTrainLoss': epoch_train_loss,
                'finalTrainAcc': epoch_train_acc,
                'finalValLoss': epoch_val_loss if val_loader else None,
                'finalValAcc': epoch_val_acc if val_loader else None
            }
            socketio.emit('training_status_update', success_message)
            update_task_status(task_id, 2, end_time=end_time) # 更新数据库状态为成功
            logger.info(f"训练任务 {task_id} 成功完成")
            
            return history
            
        except Exception as e:
            logger.error(f"训练失败: {str(e)}")
            # 更新任务状态为失败
            update_task_status(task_id, 2, end_time=datetime.now(), error_msg=str(e))
            
            # 发送失败消息
            failure_message = {
                'taskId': task_id,
                'status': 2, # 失败
                'endTime': datetime.now().isoformat(),
                'message': f'训练失败: {str(e)}'
            }
            socketio.emit('training_status_update', failure_message)
            raise
        finally:
            # 清理临时文件等操作可以在这里添加
            pass
            
            # 计算总训练时间
            total_time = time.time() - start_time
            logger.info(f"训练完成，总耗时: {total_time:.2f}秒")
            
            # 更新训练结束时间、精度和损失值
            from datetime import datetime
            final_accuracy = history['val_acc'][-1] if history['val_acc'] else history['train_acc'][-1]
            final_loss = history['val_loss'][-1] if history['val_loss'] else history['train_loss'][-1]
            
            # 更新任务状态并发布消息
            update_task_status(task_id, 3, end_time=datetime.now(), accuracy=final_accuracy, loss=final_loss)
            completion_message = {
                'taskId': task_id,
                'status': 3, # 完成
                'endTime': datetime.now().isoformat(),
                'accuracy': final_accuracy,
                'loss': final_loss,
                'message': '训练成功完成'
            }
            socketio.emit('training_status_update', completion_message)
            
            # 清理临时数据集目录
            if user_id:
                import shutil
                temp_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) / 'temp_datasets' / str(user_id) / str(task_id)
                if temp_dir.exists():
                    try:
                        shutil.rmtree(temp_dir)
                        logger.info(f"已清理临时数据集目录: {temp_dir}")
                    except Exception as e:
                        logger.warning(f"清理临时数据集目录失败: {str(e)}")
            
            return history
    
    def save_model(self, model_name=None, user_id=None, task_id=None):
        """
        保存模型
        
        Args:
            model_name (str, optional): 模型名称，如果为None则使用初始化时的名称
            user_id (str, optional): 用户ID，用于指定保存路径
            task_id (str, optional): 任务ID，用于指定保存路径,用于更新数据库中的model_path字段
        """
        if model_name is None:
            model_name = self.model_name
        
        # 设置模型保存路径
        if user_id:
            # 使用用户ID和任务ID构建保存路径
            save_dir = MODEL_DIR / str(user_id)
            if task_id:
                save_dir = save_dir / str(task_id)
            os.makedirs(save_dir, exist_ok=True)
            save_path = save_dir / f"{model_name}.pt"
        else:
            save_path = MODEL_DIR / f"{model_name}.pt"
        
        # 保存模型
        try:
            # 使用CPU版本的状态字典以避免序列化问题
            model_state = {k: v.cpu() for k, v in self.model.state_dict().items()}
            optimizer_state = {k: v.cpu() if torch.is_tensor(v) else v for k, v in self.optimizer.state_dict().items()}
            
            # 使用pickle协议版本2，提高兼容性
            torch.save({
                'model_state_dict': model_state,
                'optimizer_state_dict': optimizer_state,
                'scheduler_state_dict': self.scheduler.state_dict(),
                'num_classes': self.num_classes
            }, save_path, _use_new_zipfile_serialization=False)
            logger.info(f"模型已保存到: {save_path}")
            
            # 如果有任务ID，更新数据库中的model_path
            if task_id:
                from utils.db_utils import get_db
                conn = get_db()
                try:
                    with conn.cursor() as cursor:
                        # 先获取当前的parameters，确保不丢失classes信息
                        cursor.execute('SELECT parameters FROM training_task WHERE id = %s', (task_id,))
                        row = cursor.fetchone()
                        if row and row.get('parameters'):
                            try:
                                # 记录当前parameters，确保后续操作不会丢失classes信息
                                logger.info(f"保存模型前的parameters: {row['parameters']}")
                                
                                # 解析parameters字段
                                params = {}
                                try:
                                    params = json.loads(row['parameters'])
                                except json.JSONDecodeError:
                                    logger.warning(f"参数格式无效，将使用空字典")
                                    params = {}
                                except Exception as e:
                                    logger.error(f"解析parameters字段失败: {e}")
                                    params = {}
                                
                                # 如果训练数据集中有类别信息，添加到parameters中
                                if hasattr(self, 'train_dataset') and hasattr(self.train_dataset, 'class_names'):
                                    # 将classes和num_classes信息添加到参数中
                                    # 确保不覆盖现有参数，只添加classes信息
                                    params['classes'] = [str(cls) for cls in self.train_dataset.class_names]
                                    params['num_classes'] = len(self.train_dataset.class_names)
                                    logger.info(f"添加classes信息: {params['classes']}")
                                    logger.info(f"添加num_classes信息: {params['num_classes']}")
                                    
                                    # 更新数据库
                                    params_json = json.dumps(params)
                                    cursor.execute(
                                        'UPDATE training_task SET parameters = %s WHERE id = %s',
                                        (params_json, task_id)
                                    )
                                    conn.commit()
                                    affected_rows = cursor.rowcount
                                    logger.info(f"已更新training_task.parameters: 影响行数={affected_rows}")
                            except Exception as e:
                                logger.error(f"更新parameters失败: {str(e)}")
                        
                        # 更新training_task表中的model_path字段、progress字段
                        cursor.execute(
                            'UPDATE training_task SET model_path = %s, progress = 100 WHERE id = %s',
                            (str(save_path), task_id)
                        )
                        conn.commit()
                        logger.info(f"已更新任务 {task_id} 的模型路径")
                        
                        # 将模型信息插入到classification_model表中
                        try:
                            # 获取训练任务信息
                            cursor.execute('SELECT user_id, model_name, parameters FROM training_task WHERE id = %s', (task_id,))
                            task_info = cursor.fetchone()
                            
                            if task_info:
                                user_id = task_info['user_id']
                                model_name = task_info['model_name']
                                parameters = task_info['parameters']
                                
                                # 解析parameters
                                params_dict = {}
                                try:
                                    params_dict = json.loads(parameters)
                                except Exception as e:
                                    logger.error(f"解析parameters失败: {str(e)}")
                                
                                # 获取classes信息
                                classes = None
                                if 'classes' in params_dict:
                                    classes = json.dumps(params_dict['classes'])
                                
                                # 计算模型精度（如果有验证数据）
                                accuracy = None
                                if 'valAcc' in params_dict:
                                    accuracy = params_dict['valAcc']
                                elif hasattr(self, 'best_val_acc'):
                                    accuracy = self.best_val_acc
                                
                                # 检查是否已经为当前训练任务插入过模型记录
                                # 由于一个训练任务会保存多个模型文件（best、final等），但我们只需要在数据库中保存一条记录
                                # 所以我们检查是否已经存在相同训练任务ID的其他模型记录
                                cursor.execute('SELECT id FROM classification_model WHERE model_path LIKE %s', (f'%{task_id}%',))
                                existing_model = cursor.fetchone()
                                
                                if existing_model:
                                    # 更新现有模型，包括模型路径
                                    cursor.execute(
                                        'UPDATE classification_model SET model_name = %s, model_path = %s, model_type = %s, description = %s, '
                                        'accuracy = %s, classes = %s, parameters = %s, update_time = NOW() '
                                        'WHERE id = %s',
                                        (model_name, str(save_path), 'CNN', f'训练的{model_name}模型', accuracy, classes, parameters, existing_model['id'])
                                    )
                                    logger.info(f"已更新classification_model表中的模型信息，ID={existing_model['id']}，新路径={save_path}")
                                    # 记录日志，帮助调试
                                    logger.info(f"模型更新成功，任务ID={task_id}, 模型名称={model_name}")

                                else:
                                    # 只有在没有现有记录时才插入新模型
                                    # 这样可以确保每个训练任务只插入一条记录到classification_model表中
                                    # 即使训练过程中保存了多个模型文件（best、final等）
                                    cursor.execute(
                                        'INSERT INTO classification_model (user_id, model_name, model_path, model_type, description, '
                                        'accuracy, classes, parameters, is_default, status, create_time, update_time) '
                                        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())',
                                        (user_id, model_name, str(save_path), 'CNN', f'训练的{model_name}模型', 
                                         accuracy, classes, parameters, 0, 1)
                                    )
                                    logger.info(f"已将模型信息插入到classification_model表中，路径={save_path}")
                                    # 记录日志，帮助调试
                                    logger.info(f"模型插入成功，任务ID={task_id}, 模型名称={model_name}")

                                
                                conn.commit()
                        except Exception as e:
                            logger.error(f"保存模型信息到classification_model表失败: {str(e)}")
                            # 不抛出异常，确保主流程不受影响
                finally:
                    conn.close()
            
            return str(save_path)
        except Exception as e:
            logger.error(f"保存模型失败: {str(e)}")
            raise
    
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