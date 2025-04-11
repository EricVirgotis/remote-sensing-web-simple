from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import uuid
import hashlib
from werkzeug.utils import secure_filename
from config import FILE_STORE_CONFIG

app = Flask(__name__, static_folder=FILE_STORE_CONFIG['base_path'], static_url_path='/api/file')
CORS(app)

def ensure_directory(bucket_name):
    """确保存储目录存在"""
    directory = os.path.join(FILE_STORE_CONFIG['base_path'], bucket_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

@app.route('/api/file/upload/<bucket>', methods=['POST'])
def upload_file(bucket):
    """上传文件"""
    if 'file' not in request.files:
        return jsonify({'code': 400, 'msg': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 400, 'msg': '没有选择文件'}), 400
    
    print(f"file.content_type: {file.content_type}")
    
    # 验证文件类型
    if file.content_type not in FILE_STORE_CONFIG['allowed_types']:
        return jsonify({'code': 400, 'msg': '不支持的文件类型'}), 400
    
    # 一次性读取文件内容
    content = file.read()
    
    # 验证文件大小
    if len(content) > FILE_STORE_CONFIG['max_size']:
        return jsonify({'code': 400, 'msg': '文件大小超过限制'}), 400
    
    # 检查是否是缓存文件
    is_cache = request.form.get('is_cache') == 'true'
    print(f"is_cache: {is_cache}")

    # 获取用户ID，从请求头或默认为'default'
    user_id = request.headers.get('X-User-ID', 'default')
    
    # 生成文件名并保存
    # 获取扩展名
    extension = os.path.splitext(file.filename)[1]  # 直接从原始文件名获取扩展名, 已经带点，例如.pdf
    if is_cache:
        # 如果是缓存文件，直接使用原文件名（避免使用文件内容的MD5作为缓存key，因为在网络传输过程中，文件内容可能发生变化，比如文件被重新组织）
        filename = file.filename
        print(f"cache_filename: {filename}")
    else:
        # 否则，使用uuid作为文件名
        filename = str(uuid.uuid4()) + extension
        print(f"filename: {filename}")
    
    # 创建用户专属目录
    user_directory = os.path.join(bucket, user_id)
    directory = ensure_directory(user_directory)
    file_path = os.path.join(directory, filename)
    
    # 使用已读取的内容写入文件
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # 返回文件访问URL，包含用户ID路径
    object_key = f"{user_id}/{filename}"
    url = f"{FILE_STORE_CONFIG['access_url']}/{bucket}/{object_key}"
    return jsonify({
        'code': 200,
        'msg': '上传成功',
        'data': {
            'url': url,
            'bucket': bucket,
            'objectKey': object_key
        }
    })

@app.route('/api/file/<bucket>/<path:object_key>', methods=['GET'])
def get_file(bucket, object_key):
    """获取文件"""
    file_path = os.path.join(FILE_STORE_CONFIG['base_path'], bucket, object_key)
    if not os.path.exists(file_path):
        return jsonify({'code': 404, 'msg': '文件不存在'}), 404
    return send_file(file_path)

@app.route('/api/file/<bucket>/<path:object_key>', methods=['DELETE'])
def delete_file(bucket, object_key):
    """删除文件"""
    file_path = os.path.join(FILE_STORE_CONFIG['base_path'], bucket, object_key)
    if os.path.exists(file_path):
        os.remove(file_path)
    return jsonify({
        'code': 200,
        'msg': '删除成功'
    })

if __name__ == '__main__':
    # 确保基础存储目录存在
    if not os.path.exists(FILE_STORE_CONFIG['base_path']):
        os.makedirs(FILE_STORE_CONFIG['base_path'])
    app.run(port=5001)