# -*- coding: utf-8 -*-
"""
文件工具模块

提供文件操作相关的辅助功能
"""

import os
import logging
import shutil
import zipfile
from pathlib import Path
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

# 允许的图像文件扩展名
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.img'}

def is_allowed_file(filename, allowed_extensions=None):
    """
    检查文件扩展名是否允许
    
    Args:
        filename (str): 文件名
        allowed_extensions (set, optional): 允许的扩展名集合，如果为None则使用默认图像扩展名
        
    Returns:
        bool: 是否允许
    """
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_IMAGE_EXTENSIONS
        
    return Path(filename).suffix.lower() in allowed_extensions

def safe_filename(filename):
    """
    生成安全的文件名
    
    Args:
        filename (str): 原始文件名
        
    Returns:
        str: 安全的文件名
    """
    return secure_filename(filename)

def ensure_dir(directory):
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory (str or Path): 目录路径
        
    Returns:
        Path: 目录路径对象
    """
    directory = Path(directory)
    os.makedirs(directory, exist_ok=True)
    return directory

def extract_zip(zip_path, extract_to=None, delete_zip=False):
    """
    解压ZIP文件
    
    Args:
        zip_path (str or Path): ZIP文件路径
        extract_to (str or Path, optional): 解压目标目录，如果为None则解压到ZIP文件所在目录
        delete_zip (bool): 解压后是否删除ZIP文件
        
    Returns:
        Path: 解压目标目录路径
    """
    try:
        zip_path = Path(zip_path)
        
        # 确定解压目标目录
        if extract_to is None:
            extract_to = zip_path.parent
        else:
            extract_to = Path(extract_to)
            ensure_dir(extract_to)
        
        # 解压文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        # 删除ZIP文件（如果需要）
        if delete_zip:
            os.remove(zip_path)
        
        return extract_to
        
    except Exception as e:
        logger.error(f"解压ZIP文件失败: {str(e)}")
        raise

def get_file_info(file_path):
    """
    获取文件信息
    
    Args:
        file_path (str or Path): 文件路径
        
    Returns:
        dict: 文件信息
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            return None
        
        return {
            'name': file_path.name,
            'path': str(file_path),
            'size': file_path.stat().st_size,
            'created_time': file_path.stat().st_ctime,
            'modified_time': file_path.stat().st_mtime,
            'extension': file_path.suffix.lower()
        }
        
    except Exception as e:
        logger.error(f"获取文件信息失败: {str(e)}")
        return None

def list_files(directory, pattern=None, recursive=False):
    """
    列出目录中的文件
    
    Args:
        directory (str or Path): 目录路径
        pattern (str, optional): 文件名匹配模式，如 '*.jpg'
        recursive (bool): 是否递归遍历子目录
        
    Returns:
        list: 文件路径列表
    """
    try:
        directory = Path(directory)
        
        if not directory.exists() or not directory.is_dir():
            return []
        
        if recursive:
            if pattern:
                return [str(p) for p in directory.glob(f'**/{pattern}')]
            else:
                return [str(p) for p in directory.glob('**/*') if p.is_file()]
        else:
            if pattern:
                return [str(p) for p in directory.glob(pattern)]
            else:
                return [str(p) for p in directory.iterdir() if p.is_file()]
                
    except Exception as e:
        logger.error(f"列出文件失败: {str(e)}")
        return []

def delete_file(file_path):
    """
    删除文件
    
    Args:
        file_path (str or Path): 文件路径
        
    Returns:
        bool: 是否成功删除
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            return False
        
        if file_path.is_file():
            os.remove(file_path)
        elif file_path.is_dir():
            shutil.rmtree(file_path)
            
        return True
        
    except Exception as e:
        logger.error(f"删除文件失败: {str(e)}")
        return False