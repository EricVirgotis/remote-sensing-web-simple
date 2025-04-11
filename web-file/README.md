# 文件对象存储服务

## 项目介绍
本项目是文件对象存储服务，基于 Python Flask 开发，提供了文件上传、下载、删除等功能的 RESTful API 接口。主要用于处理系统中的图片、视频等文件存储需求。

## 技术栈
- Python 3.8+
- Flask 2.0+
- Flask-CORS
- Werkzeug

## 功能特性
1. 文件上传
   - 支持单文件上传
   - 文件类型限制
   - 文件大小限制
   - 支持缓存文件标记

2. 文件下载
   - 文件直接下载
   - 支持通过URL访问

3. 文件管理
   - 文件删除
   - 按bucket分类存储

4. 安全特性
   - 文件类型校验
   - 文件大小限制
   - 文件名安全处理

## 项目结构
```
web-file/
├── config.py           # 配置文件
├── app.py             # 主程序
└── requirements.txt    # 依赖文件
```

## 开发环境要求
- Python 3.8+
- pip

## 本地开发
1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 运行服务
```bash
python app.py
```

## 配置说明
主要配置项（config.py）：
- base_path：文件存储基础路径
- access_url：文件访问URL前缀（http://localhost:5001/api/file）
- allowed_types：各存储桶允许的文件类型
  - avatars：image/jpeg, image/png, image/gif
  - images：image/jpeg, image/png
  - temp：支持更多类型，包括图片和文档
- max_sizes：各存储桶的文件大小限制
  - avatars：2MB
  - images：10MB
  - temp：20MB

## 部署说明
1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 使用生产服务器（如gunicorn）运行
```bash
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

## 注意事项
- 默认端口：5001
- 文件上传大小限制：根据不同bucket配置
- 支持的文件类型：根据不同bucket配置
- 确保文件存储目录具有正确的读写权限 