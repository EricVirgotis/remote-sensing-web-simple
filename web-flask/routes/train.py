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
from utils.db_utils import get_db, update_task_status, get_dataset_info, get_task_parameters # 导入 get_task_parameters

logger = logging.getLogger(__name__)

# 创建蓝图
train_bp = Blueprint('train', __name__)

@train_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "training"})

# 数据集目录
DATASET_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / '/temp_datasets'
os.makedirs(DATASET_DIR, exist_ok=True)

# 训练结果目录
TRAIN_RESULT_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / '../train_results'
os.makedirs(TRAIN_RESULT_DIR, exist_ok=True)

@train_bp.route('/train-task', methods=['POST'])
def create_train_task():
    """
    创建训练任务
    
    Returns:
        JSON: 训练任务ID
    """
    try:
        data = request.get_json()
        
        # 验证必填参数
        required_fields = ['task_name', 'dataset_name', 'epochs', 'batch_size', 'learning_rate', 'model_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必填参数: {field}'
                }), 400
                
        # 检查模型名称是否有效
        valid_models = ['LeNet-5', 'AlexNet', 'VGGNet-16', 'GoogleNet', 'ResNet50']
        if data['model_name'] not in valid_models:
            return jsonify({
                'status': 'error',
                'message': f'无效的模型名称，支持的模型: {", ".join(valid_models)}'
            }), 400
            
        # 这里需要添加实际的训练任务创建逻辑
        return jsonify({
            'status': 'success',
            'data': 1  # 示例返回的训练任务ID
        })
    except Exception as e:
        logger.error(f'创建训练任务失败: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': '创建训练任务失败'
        }), 500

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

        # 获取用户ID
        user_id = request.form.get('user_id', None)
        if not user_id:
            return jsonify({
              'status': 'error',
              'message': '缺少用户ID'
            }), 400
        else:
            user_id = int(user_id)  # 确保 user_id 是整数
        
        # 获取数据集名称
        dataset_name = request.form.get('dataset_name', None)
        if not dataset_name:
            # 使用时间戳作为数据集名称
            dataset_name = f"dataset_{int(time.time())}"
        else:
            # 安全处理数据集名称
            dataset_name = secure_filename(dataset_name)
        
        # 创建数据集目录
        dataset_dir = DATASET_DIR / str(user_id) / dataset_name
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
        epochs = data.get('epochs') # 先获取原始值
        batch_size = data.get('batch_size') # 先获取原始值
        use_pretrained = data.get('usePretrained', True) # 获取 use_pretrained 参数，默认为 True
        task_id = data.get('taskId')
        dataset_id = data.get('datasetId')

        # --- 参数验证和回退逻辑 ---
        db_params = None
        if task_id:
            db_params = get_task_parameters(task_id)

        # 验证 epochs
        valid_epochs = False
        if epochs is not None:
            try:
                epochs = int(epochs)
                if epochs > 0:
                    valid_epochs = True
            except (ValueError, TypeError):
                pass # 转换失败，尝试从数据库获取

        if not valid_epochs and db_params:
            epochs_from_db = db_params.get('epochs')
            if epochs_from_db is not None:
                try:
                    epochs = int(epochs_from_db)
                    if epochs > 0:
                        valid_epochs = True
                except (ValueError, TypeError):
                    pass # 数据库中的值也无效

        if not valid_epochs:
            epochs = 30 # 使用默认值
            logger.warning(f"任务 {task_id}: epochs 无效或缺失，使用默认值 30")

        # 验证 batch_size
        valid_batch_size = False
        if batch_size is not None:
            try:
                batch_size = int(batch_size)
                if batch_size > 0:
                    valid_batch_size = True
            except (ValueError, TypeError):
                pass # 转换失败，尝试从数据库获取

        if not valid_batch_size and db_params:
            batch_size_from_db = db_params.get('batchSize') # 注意数据库中可能是驼峰命名
            if batch_size_from_db is None:
                 batch_size_from_db = db_params.get('batch_size') # 尝试下划线命名

            if batch_size_from_db is not None:
                try:
                    batch_size = int(batch_size_from_db)
                    if batch_size > 0:
                        valid_batch_size = True
                except (ValueError, TypeError):
                    pass # 数据库中的值也无效

        if not valid_batch_size:
            batch_size = 32 # 使用默认值
            logger.warning(f"任务 {task_id}: batch_size 无效或缺失，使用默认值 32")
        # --- 参数验证结束 ---

        if dataset_id is None:
            if task_id:
                update_task_status(task_id=task_id, status=2, error_message='缺少必填参数: datasetId')
            return jsonify({
                'status': 'error',
                'message': '缺少必填参数: datasetId'
            }), 400
        if not dataset_name:
            if task_id:
                update_task_status(task_id=task_id, status=2, error_message='缺少数据集名称')
            return jsonify({
                'status': 'error',
                'message': '缺少数据集名称'
            }), 400

        if not model_name:
            if task_id:
                update_task_status(task_id=task_id, status=2, error_message='缺少模型名称')
            return jsonify({
                'status': 'error',
                'message': '缺少模型名称'
            }), 400

        # 从数据库获取数据集信息
        dataset_info = get_dataset_info(dataset_id)
        if not dataset_info:
            if task_id:
                update_task_status(task_id=task_id, status=2, error_message=f"数据集 ID {dataset_id} 不存在")
            return jsonify({
                'status': 'error',
                'message': f"数据集 ID {dataset_id} 不存在"
            }), 404

        # --- 接下来的逻辑中使用 dataset_info['dataset_name'] 等 ---
        # 使用时间戳和用户ID构建数据集路径 (这部分逻辑需要确认是否正确)
        # 注意：get_dataset_info 返回的是字典，应该用 dataset_info['xxx'] 获取值
        timestamp = dataset_info.get('timestamp')
        user_id = dataset_info.get('user_id')
        db_dataset_name = dataset_info.get('dataset_name') # 从数据库获取的名字

        # 这里获取数据集路径的逻辑似乎有点问题，通常路径是直接存在数据库里的
        # training_dataset 表里应该有 dataset_path 字段
        # 假设 training_dataset 表有 dataset_path 字段
        dataset_zip_path_from_db = dataset_info.get('dataset_path') # 尝试从 get_dataset_info 获取路径
        if not dataset_zip_path_from_db:
             # 如果 get_dataset_info 没返回路径，需要修改 get_dataset_info 或这里的逻辑
             # 再次查询数据库获取路径
             conn = get_db()
             try:
                 with conn.cursor() as cursor:
                     cursor.execute('SELECT dataset_path FROM training_dataset WHERE id = %s', (dataset_id,))
                     row = cursor.fetchone()
                     if row:
                         dataset_zip_path_from_db = row['dataset_path']
                     else:
                         # 处理找不到路径的情况
                         if task_id: update_task_status(task_id=task_id, status=2, error_message=f"无法获取数据集 ID {dataset_id} 的路径")
                         return jsonify({'status': 'error','message': f"无法获取数据集 ID {dataset_id} 的路径"}), 404
             finally:
                 conn.close()

        # 确保路径存在
        dataset_path = Path(dataset_zip_path_from_db) # 使用数据库中的路径
        if not dataset_path.exists() or not dataset_path.is_file():
             if task_id: update_task_status(task_id=task_id, status=2, error_message=f"数据集文件不存在: {dataset_path}")
             return jsonify({
                'status': 'error',
                'message': f"数据集文件不存在: {dataset_path}"
            }), 404

        # 创建临时工作目录
        temp_dir_base = Path('./temp_datasets')
        os.makedirs(temp_dir_base, exist_ok=True)
        dataset_dir = temp_dir_base / str(task_id)
        if os.path.exists(dataset_dir):
            shutil.rmtree(dataset_dir)
        os.makedirs(dataset_dir, exist_ok=True)

        # 解压数据集
        try:
            with zipfile.ZipFile(dataset_path, 'r') as zip_ref:
                zip_ref.extractall(dataset_dir)
        except zipfile.BadZipFile:
            if task_id:
                update_task_status(task_id=task_id, status=2, error_message=f"数据集文件损坏或非ZIP格式: {dataset_path}")
            shutil.rmtree(dataset_dir)
            return jsonify({'status': 'error', 'message': f"数据集文件损坏或非ZIP格式: {dataset_path}"}), 400
        except Exception as e:
            if task_id:
                update_task_status(task_id=task_id, status=2, error_message=f"解压数据集失败: {e}")
            shutil.rmtree(dataset_dir)
            return jsonify({'status': 'error', 'message': f"解压数据集失败: {e}"}), 500

        # 检查数据集结构
        train_dir = dataset_dir / 'train'
        val_dir = dataset_dir / 'val'
        
        # 如果没有train目录，创建train和val目录结构
        if not train_dir.is_dir():
            os.makedirs(train_dir, exist_ok=True)
            os.makedirs(val_dir, exist_ok=True)
            
            # 遍历解压目录，查找图片文件
            image_files = []
            for root, _, files in os.walk(dataset_dir):
                if 'train' not in root and 'val' not in root:  # 跳过已经在train或val目录下的文件
                    for file in files:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                            image_files.append(Path(root) / file)
            
            if not image_files:
                if task_id:
                    update_task_status(task_id=task_id, status=2, error_message="未找到任何图片文件")
                shutil.rmtree(dataset_dir)
                return jsonify({
                    'status': 'error',
                    'message': '未找到任何图片文件'
                }), 400
            
            # 获取所有图片所在的直接父目录名称作为类别
            classes = set()
            for img_path in image_files:
                class_name = img_path.parent.name
                if class_name and class_name != dataset_dir.name:
                    classes.add(class_name)
            
            # 如果没有明确的类别目录，将所有图片放在一个默认类别下
            if not classes:
                classes = {'default_class'}
            
            # 创建类别目录并移动图片
            for class_name in classes:
                train_class_dir = train_dir / class_name
                val_class_dir = val_dir / class_name
                os.makedirs(train_class_dir, exist_ok=True)
                os.makedirs(val_class_dir, exist_ok=True)
                
                # 获取该类别的图片
                class_images = [img for img in image_files 
                              if img.parent.name == class_name or 
                              (class_name == 'default_class' and img.parent.name == dataset_dir.name)]
                
                # 按7:3比例划分训练集和验证集
                import random
                random.shuffle(class_images)
                split_idx = int(len(class_images) * 0.7)
                
                # 移动文件到对应目录
                for img in class_images[:split_idx]:
                    shutil.copy2(img, train_class_dir / img.name)
                for img in class_images[split_idx:]:
                    shutil.copy2(img, val_class_dir / img.name)
            
            # 清理原始图片
            for img in image_files:
                if img.exists() and img.parent != train_dir and img.parent != val_dir:
                    os.remove(img)

        # 验证训练目录结构
        if not train_dir.is_dir() or not any(d.is_dir() for d in train_dir.iterdir()):
            if task_id:
                update_task_status(task_id=task_id, status=2, error_message=f"数据集结构无效，需要包含train目录和至少一个类别子目录")
            shutil.rmtree(dataset_dir)
            return jsonify({
                'status': 'error',
                'message': '数据集结构无效，需要包含train目录和至少一个类别子目录'
            }), 400

        # 准备训练数据和参数
        from algo.trainer import ModelTrainer
        import json
        
        try:
            # 更新任务状态为训练中
            if task_id:
                update_task_status(task_id=task_id, status=1)  # 1表示训练中

            # 准备训练数据
            train_data = {
                'images': [str(f) for f in train_dir.rglob('*') if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']],
                'labels': [f.parent.name for f in train_dir.rglob('*') if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
            }
            
            val_data = {
                'images': [str(f) for f in val_dir.rglob('*') if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']],
                'labels': [f.parent.name for f in val_dir.rglob('*') if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
            }
            
            # 获取类别列表和数量
            classes = sorted(list(set(train_data['labels'])))
            num_classes = len(classes)
            
            # 如果有任务ID，将classes信息添加到training_task.parameters中
            if task_id:
                # 获取当前parameters值
                conn = get_db()
                try:
                    with conn.cursor() as cursor:
                        cursor.execute('SELECT parameters FROM training_task WHERE id = %s', (task_id,))
                        row = cursor.fetchone()
                        
                        # 解析parameters字段
                        params = {}
                        if row and row.get('parameters'):
                            try:
                                params = json.loads(row['parameters'])
                                logger.info(f"获取到现有参数: {params}")
                            except json.JSONDecodeError:
                                logger.warning(f"参数格式无效，将使用空字典")
                                params = {}
                            except Exception as e:
                                logger.error(f"解析parameters字段失败: {e}")
                                params = {}
                        
                        # 更新parameters字段
                        try:
                            # 记录更新前后的参数变化
                            logger.info(f"更新前的参数: {params}")
                            
                            # 将classes和num_classes信息添加到参数中
                            # 确保不覆盖现有参数，只添加classes信息
                            params['classes'] = [str(cls) for cls in classes]
                            params['num_classes'] = num_classes
                            logger.info(f"添加classes信息: {classes}")
                            logger.info(f"添加num_classes信息: {num_classes}")
                            
                            # 更新数据库
                            params_json = json.dumps(params)
                            cursor.execute(
                                'UPDATE training_task SET parameters = %s WHERE id = %s',
                                (params_json, task_id)
                            )
                            conn.commit()
                            affected_rows = cursor.rowcount
                            logger.info(f"已更新training_task.parameters: 影响行数={affected_rows}")
                            
                            # 验证更新是否成功
                            cursor.execute('SELECT parameters FROM training_task WHERE id = %s', (task_id,))
                            verify_row = cursor.fetchone()
                            if verify_row and verify_row.get('parameters'):
                                try:
                                    verify_params = json.loads(verify_row['parameters'])
                                    if 'classes' in verify_params:
                                        logger.info(f"验证成功: classes信息已正确保存到数据库: {verify_params['classes']}")
                                    else:
                                        logger.warning(f"验证失败: 数据库中未找到classes信息")
                                except json.JSONDecodeError:
                                    logger.error(f"验证失败: 无法解析数据库中的parameters字段")
                            else:
                                logger.error(f"验证失败: 无法从数据库获取更新后的parameters字段")
                        except Exception as e:
                            logger.error(f"更新parameters字段失败: {e}")
                finally:
                    conn.close()
            
            # 创建训练器实例
            trainer = ModelTrainer(
                model_name=model_name,
                num_classes=num_classes,
                use_pretrained=use_pretrained # 传递 use_pretrained 参数
            )
            
            # 开始训练
            training_result = trainer.train(
                train_data=train_data,
                val_data=val_data,
                epochs=epochs, # 确保传递的是整数 epochs
                batch_size=batch_size, # 确保传递的是整数 batch_size
                task_id=task_id,
                user_id=user_id,
            )
            
            # 保存训练结果
            result_dir = TRAIN_RESULT_DIR / str(user_id) / str(task_id)
            os.makedirs(result_dir, exist_ok=True)
            result_file = result_dir / f"{model_name}_result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(training_result, f, indent=2)
            
            # 更新任务状态为完成
            if task_id:
                update_task_status(
                    task_id=task_id,
                    status=3  # 3表示训练完成
                )
            
            # 清理临时目录
            shutil.rmtree(dataset_dir)
            
            return jsonify({
                'status': 'success',
                'message': '训练完成',
                'data': training_result
            })
            
        except Exception as train_error:
            # 训练过程中出现错误
            logger.error(f"训练过程错误: {str(train_error)}", exc_info=True)
            if task_id:
                update_task_status(task_id=task_id, status=2, error_message=str(train_error))
            # 清理临时目录
            shutil.rmtree(dataset_dir)
            raise train_error  # 继续向上抛出异常

    except Exception as e:
        logger.error(f"训练失败: {str(e)}", exc_info=True) # 记录详细堆栈
        # 更新任务状态为失败(2)
        # 确保 task_id 存在才更新
        task_id_for_update = data.get('taskId') if 'data' in locals() else None
        if task_id_for_update:
             update_task_status(task_id=task_id_for_update, status=2, error_message=str(e))
        return jsonify({
            'status': 'error',
            'message': f"训练失败: {str(e)}",
            'task_status': 2  # 2表示训练失败
        }), 500

# --- 同时修改 db_utils.py ---
# 确保 get_dataset_info 返回 dataset_path
def get_dataset_info(dataset_id):
    """
    获取数据集信息

    Args:
        dataset_id (int): 数据集ID

    Returns:
        dict: 数据集信息，包含时间戳和用户ID等
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'SELECT * FROM training_dataset WHERE id = %s AND deleted = 0',
                (dataset_id,)
            )
            row = cursor.fetchone()

            if row:
                return {
                    'id': row['id'],
                    'dataset_name': row['dataset_name'],
                    'user_id': row['user_id'],
                    'dataset_path': row['dataset_path'], # <-- 添加返回路径
                    'timestamp': int(row['create_time'].timestamp()) if row['create_time'] else None, # 处理时间可能为 NULL
                    'status': row['status'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None
                }
            return None
    finally:
        conn.close()

@train_bp.route('/train-task/<int:task_id>', methods=['DELETE'])
def delete_train_task(task_id):
    """
    删除训练任务
    
    Args:
        task_id (int): 任务ID
        
    Returns:
        JSON: 删除结果
    """
    try:
        # 删除数据库记录
        from utils.db_utils import delete_train_task
        if delete_train_task(task_id):
            # 删除成功，返回成功响应
            return jsonify({
                'code': 200,
                'msg': '训练任务删除成功'
            })
        else:
            # 未找到任务，返回404错误
            return jsonify({
                'code': 404,
                'msg': '未找到该训练任务'
            }), 404
    except Exception as e:
        logger.error(f'删除训练任务失败: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': '删除训练任务失败'
        }), 500

@train_bp.route('/retry/<int:task_id>', methods=['POST'])
def retry_training(task_id):
    """
    重试失败的训练任务
    
    Args:
        task_id (int): 训练任务ID
        
    Returns:
        JSON: 重试结果
    """
    try:
        # 获取任务信息
        conn = get_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    'SELECT * FROM training_task WHERE id = %s',
                    (task_id,)
                )
                task = cursor.fetchone()
                
                if not task:
                    return jsonify({
                        'status': 'error',
                        'message': f'训练任务 {task_id} 不存在'
                    }), 404
                
                # 只有失败的任务才能重试
                if task['status'] != 2:  # 2表示失败状态
                    return jsonify({
                        'status': 'error',
                        'message': '只能重试失败的训练任务'
                    }), 400
                
                # 重置任务状态
                update_task_status(task_id=task_id, status=0)  # 0表示待训练状态
                
                # 准备重试参数
                retry_data = {
                    'taskId': task_id,
                    'datasetId': task['dataset_id'],
                    'dataset_name': task['dataset_name'],
                    'model_name': task['model_name'],
                    'epochs': task['epochs'],
                    'batch_size': task['batch_size'],
                    'learning_rate': task['learning_rate'], # 添加 learning_rate
                    'use_pretrained': task['use_pretrained'] # 添加 use_pretrained
                }
                
                # 开始重新训练
                return start_training(retry_data)
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"重试训练任务失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"重试训练任务失败: {str(e)}"
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