# -*- coding: utf-8 -*-
"""
数据库工具模块

提供数据集和训练任务的数据库操作功能
"""

import os
import json
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

def update_task_status(task_id, status, error_message=None):
    """
    更新训练任务状态
    
    Args:
        task_id (int): 任务ID
        status (int): 任务状态（0：等待中，1：进行中，2：失败，3：成功）
        error_message (str, optional): 错误信息
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
            
            cursor.execute(
                'UPDATE training_task SET task_status = %s, error_message = %s WHERE id = %s',
                (task_status, error_message, task_id)
            )
            conn.commit()
    finally:
        conn.close()