# -*- coding: utf-8 -*-
"""
CNN模型训练模块

负责基于TensorFlow/Keras的CNN模型训练
"""

import os
import logging
import time
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras import optimizers, losses, metrics, callbacks
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from pathlib import Path
from .cnn_models import create_model

logger = logging.getLogger(__name__)

# 模型存储路径
MODEL_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / '../models'

class CNNModelTrainer:
    """
    CNN模型训练器
    """
    def __init__(self, model_name, num_classes=45, input_shape=(256, 256, 3), use_pretrained=False):
        """
        初始化训练器
        
        Args:
            model_name (str): 模型名称
            num_classes (int): 类别数量
            input_shape (tuple): 输入图像形状 (高度, 宽度, 通道数)
            use_pretrained (bool): 是否使用预训练权重
        """
        # 设置GPU内存增长
        self._configure_gpu()
        
        # 创建模型
        self.model_name = model_name
        self.num_classes = num_classes
        self.input_shape = input_shape
        self.use_pretrained = use_pretrained
        self.model = create_model(model_name, input_shape, num_classes, use_pretrained)
        
        # 编译模型
        self.model.compile(
            optimizer=optimizers.Adam(learning_rate=0.001),
            loss=losses.SparseCategoricalCrossentropy(),
            metrics=['accuracy']
        )
        
        # 确保模型目录存在
        os.makedirs(MODEL_DIR, exist_ok=True)
        
        logger.info(f"初始化模型 {model_name} 完成，类别数: {num_classes}, 输入形状: {input_shape}, 使用预训练: {use_pretrained}")
    
    def _configure_gpu(self):
        """
        配置GPU内存增长
        """
        try:
            gpus = tf.config.experimental.list_physical_devices('GPU')
            if gpus:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                logger.info(f"找到 {len(gpus)} 个GPU设备，已设置内存增长")
            else:
                logger.info("未找到GPU设备，将使用CPU")
        except Exception as e:
            logger.warning(f"配置GPU失败: {str(e)}")
    
    def prepare_data_generators(self, dataset_path, batch_size=32, validation_split=0.2):
        """
        准备数据生成器
        
        Args:
            dataset_path (str): 数据集路径
            batch_size (int): 批次大小
            validation_split (float): 验证集比例
            
        Returns:
            tuple: (训练数据生成器, 验证数据生成器, 类别数量)
        """
        # 数据增强配置
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest',
            validation_split=validation_split
        )
        
        # 验证集只进行缩放
        val_datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=validation_split
        )
        
        # 训练数据生成器
        train_generator = train_datagen.flow_from_directory(
            dataset_path,
            target_size=(self.input_shape[0], self.input_shape[1]),
            batch_size=batch_size,
            class_mode='sparse',
            subset='training'
        )
        
        # 验证数据生成器
        val_generator = val_datagen.flow_from_directory(
            dataset_path,
            target_size=(self.input_shape[0], self.input_shape[1]),
            batch_size=batch_size,
            class_mode='sparse',
            subset='validation'
        )
        
        # 获取类别数量
        num_classes = len(train_generator.class_indices)
        logger.info(f"数据集包含 {num_classes} 个类别")
        
        return train_generator, val_generator, num_classes
    
    def train(self, dataset_path, epochs=10, batch_size=32, learning_rate=0.001):
        """
        训练模型
        
        Args:
            dataset_path (str): 数据集路径
            epochs (int): 训练轮数
            batch_size (int): 批次大小
            learning_rate (float): 学习率
            
        Returns:
            dict: 训练历史记录
        """
        try:
            # 准备数据生成器
            train_generator, val_generator, num_classes = self.prepare_data_generators(
                dataset_path, batch_size
            )
            
            # 如果类别数量与初始化时不同，重新创建模型
            if num_classes != self.num_classes:
                logger.info(f"类别数量不匹配，重新创建模型 (原: {self.num_classes}, 新: {num_classes})")
                self.num_classes = num_classes
                self.model = create_model(self.model_name, self.input_shape, num_classes, self.use_pretrained)
            
            # 更新学习率
            self.model.compile(
                optimizer=optimizers.Adam(learning_rate=learning_rate),
                loss=losses.SparseCategoricalCrossentropy(),
                metrics=['accuracy']
            )
            
            # 设置回调函数
            model_checkpoint = callbacks.ModelCheckpoint(
                filepath=str(MODEL_DIR / f"{self.model_name}_best.h5"),
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            )
            
            early_stopping = callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                verbose=1
            )
            
            reduce_lr = callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                verbose=1,
                min_lr=1e-6
            )
            
            tensorboard = callbacks.TensorBoard(
                log_dir=str(MODEL_DIR / 'logs' / f"{self.model_name}_{int(time.time())}"),
                histogram_freq=1
            )
            
            # 训练模型
            logger.info(f"开始训练模型 {self.model_name}, 轮数: {epochs}, 批次大小: {batch_size}, 学习率: {learning_rate}")
            start_time = time.time()
            
            history = self.model.fit(
                train_generator,
                steps_per_epoch=len(train_generator),
                epochs=epochs,
                validation_data=val_generator,
                validation_steps=len(val_generator),
                callbacks=[model_checkpoint, early_stopping, reduce_lr, tensorboard]
            )
            
            # 保存最终模型
            self.save_model()
            
            # 计算训练时间
            training_time = time.time() - start_time
            logger.info(f"模型训练完成，耗时: {training_time:.2f}秒")
            
            # 返回训练历史
            return {
                'model_name': self.model_name,
                'num_classes': self.num_classes,
                'epochs': epochs,
                'batch_size': batch_size,
                'learning_rate': learning_rate,
                'use_pretrained': self.use_pretrained,
                'training_time': training_time,
                'history': {
                    'accuracy': [float(x) for x in history.history['accuracy']],
                    'loss': [float(x) for x in history.history['loss']],
                    'val_accuracy': [float(x) for x in history.history['val_accuracy']],
                    'val_loss': [float(x) for x in history.history['val_loss']]
                }
            }
            
        except Exception as e:
            logger.error(f"训练失败: {str(e)}")
            raise
    
    def save_model(self, custom_name=None):
        """
        保存模型
        
        Args:
            custom_name (str, optional): 自定义模型名称
        """
        try:
            model_name = custom_name if custom_name else self.model_name
            model_path = MODEL_DIR / f"{model_name}.h5"
            self.model.save(str(model_path))
            logger.info(f"模型已保存: {model_path}")
            
            # 保存模型信息
            model_info = {
                'model_name': self.model_name,
                'num_classes': self.num_classes,
                'input_shape': self.input_shape,
                'use_pretrained': self.use_pretrained,
                'save_time': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            info_path = MODEL_DIR / f"{model_name}_info.json"
            with open(info_path, 'w') as f:
                json.dump(model_info, f, indent=2)
            
            logger.info(f"模型信息已保存: {info_path}")
            
        except Exception as e:
            logger.error(f"保存模型失败: {str(e)}")
            raise
    
    def evaluate(self, dataset_path, batch_size=32):
        """
        评估模型
        
        Args:
            dataset_path (str): 数据集路径
            batch_size (int): 批次大小
            
        Returns:
            dict: 评估结果
        """
        try:
            # 准备测试数据生成器
            test_datagen = ImageDataGenerator(rescale=1./255)
            test_generator = test_datagen.flow_from_directory(
                dataset_path,
                target_size=(self.input_shape[0], self.input_shape[1]),
                batch_size=batch_size,
                class_mode='sparse',
                shuffle=False
            )
            
            # 评估模型
            logger.info(f"开始评估模型 {self.model_name}")
            results = self.model.evaluate(test_generator, steps=len(test_generator))
            
            # 获取预测结果
            predictions = self.model.predict(test_generator, steps=len(test_generator))
            predicted_classes = np.argmax(predictions, axis=1)
            
            # 计算混淆矩阵
            true_classes = test_generator.classes[:len(predicted_classes)]
            class_indices = {v: k for k, v in test_generator.class_indices.items()}
            
            # 返回评估结果
            return {
                'loss': float(results[0]),
                'accuracy': float(results[1]),
                'class_indices': class_indices
            }
            
        except Exception as e:
            logger.error(f"评估失败: {str(e)}")
            raise

# 示例用法
def train_cnn_model(model_name, dataset_path, epochs=10, batch_size=32, learning_rate=0.001, use_pretrained=False):
    """
    训练CNN模型的示例函数
    
    Args:
        model_name (str): 模型名称
        dataset_path (str): 数据集路径
        epochs (int): 训练轮数
        batch_size (int): 批次大小
        learning_rate (float): 学习率
        use_pretrained (bool): 是否使用预训练权重
        
    Returns:
        dict: 训练结果
    """
    try:
        # 初始化训练器
        trainer = CNNModelTrainer(
            model_name=model_name,
            use_pretrained=use_pretrained
        )
        
        # 训练模型
        result = trainer.train(
            dataset_path=dataset_path,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate
        )
        
        return result
        
    except Exception as e:
        logger.error(f"训练CNN模型失败: {str(e)}")
        raise