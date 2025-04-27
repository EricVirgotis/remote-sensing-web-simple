import os

# 文件存储配置
FILE_STORE_CONFIG = {
    'base_path': 'D:\\Code\\System\\remote-sensing-web-simple\\remote-sensing-web-simple1\\remote-sensing-web-simple\\file_store',
    'access_url': 'http://localhost:5001/api/file',  # 文件访问URL前缀
    'allowed_types': [  # 支持的文件类型
        # 图片类型
        'image/jpeg',            # JPG/JPEG图片 (.jpg, .jpeg)
        'image/png',             # PNG图片 (.png)
        'image/gif',             # GIF图片 (.gif)
        'image/tiff',            # TIFF图片 (.tif, .tiff)
        'image/bmp',             # BMP图片 (.bmp)
        'image/x-ms-bmp',        # BMP图片的另一种MIME类型 (.bmp)
        'image/webp',            # WebP图片 (.webp)
        'image/x-icon',          # ICO图片 (.ico)
        'image/vnd.microsoft.icon', # ICO图片的另一种MIME类型 (.ico)
        'image/svg+xml',         # SVG图片 (.svg)
        'image/x-portable-pixmap', # PPM图片 (.ppm)
        'image/x-portable-graymap', # PGM图片 (.pgm)
        'image/x-portable-bitmap',  # PBM图片 (.pbm)
        'image/x-portable-anymap',  # PNM图片 (.pnm)
        
        # 文档类型
        'application/pdf',       # PDF文档 (.pdf)
        'application/msword',    # Word文档 (.doc)
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # Word文档 (.docx)
        'text/plain',           # 纯文本文件 (.txt)
        'text/markdown',        # Markdown文档 (.md)
        'text/x-markdown',      # Markdown文档的另一种MIME类型 (.md)
        'application/json',     # JSON文件 (.json)
        
        # 压缩包类型
        'application/zip',              # ZIP压缩包 (.zip)
        'application/x-zip-compressed', # ZIP压缩包的另一种MIME类型 (.zip)
        
        # 视频类型
        'video/mp4',            # MP4视频 (.mp4)
        'video/mpeg',           # MPEG视频 (.mpeg, .mpg)
        'video/quicktime',      # QuickTime视频 (.mov)
        'video/x-msvideo',      # AVI视频 (.avi)
        'video/x-ms-wmv',       # Windows Media视频 (.wmv)
        'video/x-flv',          # Flash视频 (.flv)
        'video/webm',           # WebM视频 (.webm)
        'video/3gpp',           # 3GPP视频 (.3gp)
        'video/x-matroska',     # Matroska视频 (.mkv)
        
        # 深度学习模型权重文件类型
        'application/x-hdf5',           # HDF5文件 (.h5, .hdf5) - TensorFlow/Keras权重文件
        'application/octet-stream',     # 二进制文件 - 通用类型，支持.weights.h5, .pt, .pth, .ckpt等
        'application/x-tensorflow',      # TensorFlow模型文件 (.pb, .ckpt)
        'application/x-pytorch',         # PyTorch模型文件 (.pt, .pth)
        'application/x-onnx',           # ONNX模型文件 (.onnx)
        'application/x-keras',          # Keras模型文件 (.keras)
        'application/x-savedmodel'      # TensorFlow SavedModel格式
    ],
    'max_size': 1000 * 1024 * 1024  # 最大文件大小：1000MB
}