# 模型目录

此目录用于存放遥感影像分类的预训练模型文件。

## 模型格式

支持的模型格式：
- PyTorch模型文件（.pt, .pth）

## 目录结构

```
models/
  ├── model_config.json    # 模型配置文件，包含默认模型设置
  ├── model1.pt            # 模型文件1
  ├── model2.pt            # 模型文件2
  └── ...                  # 其他模型文件
```

## 模型管理

可以通过API接口管理模型：
- 上传新模型：`POST /api/model/upload`
- 设置默认模型：`POST /api/model/set_default`
- 删除模型：`DELETE /api/model/delete/<model_name>`
- 获取模型列表：`GET /api/model/list`
- 获取模型详情：`GET /api/model/info/<model_name>`

## 模型配置

`model_config.json` 文件格式：

```json
{
  "default_model": "model_name"
}
```