# -*- coding: utf-8 -*-
"""
数据库工具模块

提供数据集和训练任务的数据库操作功能
"""

import os
import json
import logging
import pymysql
from pymysql.cursors import DictCursor

# MySQL数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'cxz20030620',
    'database': 'rs_analysis',
    'charset': 'utf8',
    'cursorclass': DictCursor
}

def get_db():
    """
    获取数据库连接
    
    Returns:
        pymysql.Connection: 数据库连接
    """
    return pymysql.connect(**DB_CONFIG)

def init_db():
    """
    初始化数据库
    注意：数据库表结构由Java后端统一管理，此处不再创建表
    """
    pass

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
                    'timestamp': int(row['create_time'].timestamp()),
                    'status': row['status'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None
                }
            return None
    finally:
        conn.close()

def update_task_status(task_id, status, error_message=None, start_time=None, end_time=None, accuracy=None, loss=None):
    """
    更新训练任务状态
    
    Args:
        task_id (int): 任务ID
        status (int): 任务状态（0：等待中，1：进行中，2：失败，3：成功）
        error_message (str, optional): 错误信息
        start_time (datetime, optional): 开始时间
        end_time (datetime, optional): 结束时间
        accuracy (float, optional): 模型精度
        loss (float, optional): 损失值
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 将状态码转换为对应的状态字符串
            status_map = {
                0: 'PENDING',
                1: 'RUNNING',
                2: 'FAILED',
                3: 'COMPLETED'
            }
            task_status = status_map.get(status, 'PENDING')
            
            # 如果状态为COMPLETED，确保保留parameters中的classes信息
            if status == 3:  # COMPLETED
                # 先获取当前的parameters
                cursor.execute('SELECT parameters FROM training_task WHERE id = %s', (task_id,))
                row = cursor.fetchone()
                current_params = None
                if row and row.get('parameters'):
                    try:
                        current_params = json.loads(row['parameters'])
                        logging.info(f"获取到当前parameters: {current_params}")
                    except json.JSONDecodeError:
                        logging.error(f"解析parameters失败: {row['parameters']}")
            
            # 构建更新字段和参数
            update_fields = ['task_status = %s']
            params = [task_status]
            
            if error_message is not None:
                update_fields.append('error_message = %s')
                params.append(error_message)
            
            if start_time is not None:
                update_fields.append('start_time = %s')
                params.append(start_time)
            
            if end_time is not None:
                update_fields.append('end_time = %s')
                params.append(end_time)
            
            if accuracy is not None:
                update_fields.append('accuracy = %s')
                params.append(accuracy)
            
            if loss is not None:
                update_fields.append('loss = %s')
                params.append(loss)
            
            # 添加task_id作为WHERE条件
            params.append(task_id)
            
            # 构建并执行SQL语句
            sql = f"UPDATE training_task SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(sql, tuple(params))
            conn.commit()
            
            # 验证更新后的parameters是否保留了classes信息
            if status == 3:  # COMPLETED
                cursor.execute('SELECT parameters FROM training_task WHERE id = %s', (task_id,))
                row = cursor.fetchone()
                if row and row.get('parameters'):
                    try:
                        updated_params = json.loads(row['parameters'])
                        if current_params and 'classes' in current_params and 'classes' not in updated_params:
                            # 如果更新后的parameters丢失了classes信息，重新添加
                            updated_params['classes'] = current_params['classes']
                            if 'num_classes' in current_params:
                                updated_params['num_classes'] = current_params['num_classes']
                            
                            # 更新parameters字段
                            cursor.execute(
                                'UPDATE training_task SET parameters = %s WHERE id = %s',
                                (json.dumps(updated_params), task_id)
                            )
                            conn.commit()
                            logging.info(f"已恢复classes信息到parameters: {updated_params['classes']}")
                    except json.JSONDecodeError:
                        logging.error(f"验证时解析parameters失败")

    finally:
        conn.close()

def get_task_parameters(task_id):
    """
    获取指定训练任务的参数

    Args:
        task_id (int): 任务ID

    Returns:
        dict: 解析后的参数字典，如果找不到或解析失败则返回 None
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'SELECT parameters FROM training_task WHERE id = %s',
                (task_id,)
            )
            row = cursor.fetchone()
            if row and row.get('parameters'):
                try:
                    return json.loads(row['parameters'])
                except json.JSONDecodeError:
                    # 处理JSON解析错误
                    return None
            return None
    finally:
        conn.close()

def delete_train_task(task_id):
    """
    删除训练任务
    
    Args:
        task_id (int): 任务ID
        
    Returns:
        bool: 删除是否成功
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 软删除训练任务
            cursor.execute(
                'UPDATE training_task SET deleted = 1 WHERE id = %s',
                (task_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()