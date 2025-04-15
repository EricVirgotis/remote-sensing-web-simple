# -*- coding: utf-8 -*-
"""
遥感影像分类任务数据准备脚本

功能：
- 解压 ZIP 文件
- 识别类别文件夹
- 按比例划分训练集和验证集
- 组织输出目录结构
- 输出类别列表和数据存放路径
- 健壮性处理

用法：
python data_prepare.py --zip_path <zip文件路径> --output_dir <输出目录>
"""

import os
import sys
import argparse
import zipfile
import shutil
import random
from pathlib import Path

IMAGE_EXTS = ['.jpg', '.jpeg', '.png']

def prepare_dataset(zip_path, output_dir):
    if not os.path.isfile(zip_path):
        print(f"错误: ZIP 文件不存在: {zip_path}")
        return None
    temp_extract_dir = Path(output_dir) / 'temp_extract'
    if temp_extract_dir.exists():
        shutil.rmtree(temp_extract_dir)
    os.makedirs(temp_extract_dir, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_dir)
    except Exception as e:
        print(f"解压失败: {e}")
        return None
    # 识别类别文件夹
    subdirs = [d for d in temp_extract_dir.iterdir() if d.is_dir()]
    if not subdirs:
        print("未找到任何类别文件夹！")
        shutil.rmtree(temp_extract_dir)
        return None
    class_names = [d.name for d in subdirs]
    # 创建输出结构
    prepared_dir = Path(output_dir) / 'prepared_data'
    train_dir = prepared_dir / 'train'
    val_dir = prepared_dir / 'validation'
    for d in [train_dir, val_dir]:
        os.makedirs(d, exist_ok=True)
    for cls in class_names:
        os.makedirs(train_dir / cls, exist_ok=True)
        os.makedirs(val_dir / cls, exist_ok=True)
    # 划分数据集并复制
    for class_dir in subdirs:
        images = [f for f in class_dir.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTS]
        random.shuffle(images)
        split_idx = int(len(images) * 0.7)
        train_imgs = images[:split_idx]
        val_imgs = images[split_idx:]
        for img in train_imgs:
            shutil.copy2(str(img), str(train_dir / class_dir.name / img.name))
        for img in val_imgs:
            shutil.copy2(str(img), str(val_dir / class_dir.name / img.name))
    # 清理临时目录
    shutil.rmtree(temp_extract_dir)
    print(f"类别列表: {class_names}")
    print(f"数据已准备好，存放路径: {prepared_dir}")
    return {'classes': class_names, 'prepared_dir': str(prepared_dir)}

def main():
    parser = argparse.ArgumentParser(description='遥感影像分类任务数据准备脚本')
    parser.add_argument('--zip_path', type=str, required=True, help='输入的ZIP文件路径')
    parser.add_argument('--output_dir', type=str, required=True, help='输出目录')
    args = parser.parse_args()
    prepare_dataset(args.zip_path, args.output_dir)

if __name__ == '__main__':
    main()