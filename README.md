# 遥感智能分类分析系统

## 项目介绍
本系统是一个基于深度学习的遥感影像智能分类分析系统。系统提供遥感影像上传、智能分类分析、结果可视化展示等功能，帮助用户快速完成遥感影像的分类分析任务。

### 主要功能
#### 用户端
- 遥感影像管理
  - 上传遥感影像文件
  - 查看历史上传记录
  - 管理遥感影像文件
- 智能分类分析
  - 选择分类模型
  - 查看分析进度
- 模型训练
  - 上传数据集
  - 训练模型
  - 查看训练结果
- 结果展示
  - 分类结果可视化
- 个人中心
  - 历史记录时间轴
  - 个人信息设置

#### 管理员端
- 用户管理
  - 用户信息维护
  - 用户权限控制
- 系统管理
  - 成果文件管理
  - 系统设置

## 技术栈

### 前端 (web-vue)
- Vue 3 - 渐进式JavaScript框架
- Element Plus - Vue 3的组件库
- ECharts - 数据可视化图表库
- TypeScript - JavaScript的超集
- Vite - 前端构建工具

### 后端 (web-springboot)
- Spring Boot 3.2.1 - Java后端框架
- MyBatis Plus 3.5.5 - ORM框架
- MySQL 8 - 关系型数据库
- Maven - 项目管理工具
- Java 17 - 编程语言
- Swagger 3 - API文档工具
- Spring MVC - Web框架
- Lombok - 简化Java代码
- Hutool - Java工具类库

### 算法服务 (web-flask)
- Python 3 - 编程语言
- Flask - Web框架
- PyTorch/TensorFlow - 深度学习框架
- GDAL - 地理空间数据处理库
- NumPy/Pandas - 数据处理库

### 文件服务 (web-file)
- Python Flask - Web框架
- 对象存储服务 - 文件存储管理

## 详细目录结构
```
├── README.md                # 项目说明文档
├── .gitignore               # Git忽略文件
├── example/                 # 示例项目
├── web-vue/                 # 前端项目
│   ├── public/             # 公共资源
│   ├── src/                # 源代码
│   │   ├── api/           # API接口
│   │   ├── assets/        # 静态资源
│   │   ├── components/    # 公共组件
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # 状态管理
│   │   ├── types/         # TypeScript类型
│   │   ├── utils/         # 工具函数
│   │   └── views/         # 页面组件
│   ├── package.json        # 项目配置
│   └── vite.config.ts      # Vite配置
├── web-springboot/         # 后端服务
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/     # Java源代码
│   │   │   └── resources/
│   │   │       ├── mapper/    # MyBatis映射文件
│   │   │       └── application.yml  # 应用配置
│   └── pom.xml             # Maven配置
├── web-flask/              # 算法服务
│   ├── algo/              # 算法模块
│   ├── routes/            # 路由
│   ├── utils/             # 工具函数
│   ├── models/            # 模型文件
│   └── requirements.txt    # Python依赖
└── web-file/              # 文件对象存储服务
    ├── app.py             # 主程序
    └── requirements.txt    # Python依赖
```

## 环境要求
- Node.js 16+
- Java 17+
- Python 3.8+
- MySQL 8+
- Maven 3.8+

## 安装部署步骤

### 1. 数据库配置
```bash
# 1. 安装MySQL 8
# 2. 创建数据库
mysql -u root -p
CREATE DATABASE rs_analysis DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# 3. 导入初始化SQL
mysql -u root -p rs_analysis < web-springboot/src/main/resources/db/init.sql
```

### 2. 后端服务 (web-springboot)
```bash
# 1. 进入后端目录
cd web-springboot

# 2. 修改数据库配置
# 编辑 src/main/resources/application.yml
# 修改数据库连接信息

# 3. 编译打包
mvn clean package

# 4. 使用mvn运行服务
mvn spring-boot:run

# 5. 运行服务（可以跳过）
java -jar target/web-springboot-1.0.0.jar
```

### 3. 算法服务 (web-flask)
```bash
# 1. 进入算法服务目录
cd web-flask

# 2. 激活conda环境
conda activate remote_sensing

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行服务
python app.py
```

### 4. 文件服务 (web-file)
```bash
# 1. 进入文件服务目录
cd web-file

# 2. 激活conda环境
conda activate remote_sensing

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行服务
python app.py
```

### 5. 前端服务 (web-vue)
```bash
# 1. 进入前端目录
cd web-vue

# 2. 安装依赖
npm install

# 3. 修改环境配置
# 编辑 .env 文件
# 确保API地址配置正确

# 4. 开发环境运行
npm run dev

# 5. 生产环境构建（可以跳过）
npm run build
```

## 访问地址
- 前端页面：http://localhost:3000
- 后端服务：http://localhost:8080
- 算法服务：http://localhost:5000
- 文件服务：http://localhost:5001

## 开发规范
1. 代码注释使用中文，保持清晰易懂
2. 配置信息统一管理，避免硬编码
3. 前端使用 Setup 语法糖，严格遵守 TypeScript 规范
4. 后端实现基础的 CRUD 操作，使用 MyBatis Plus 分页插件
5. 文件操作统一使用文件对象存储服务

## 注意事项
1. 首次运行算法服务时会进行模型预热，可能需要等待一段时间
2. 文件上传大小限制为100MB
3. 支持的遥感影像格式：TIFF、IMG等
4. 建议使用Chrome浏览器访问系统

## 系统架构

### 后端架构
后端采用分层架构设计，主要包括以下几层：
- 控制器层（Controller）：负责接收和处理HTTP请求，返回响应结果
- 服务层（Service）：实现业务逻辑，处理数据
- 数据访问层（Mapper）：与数据库交互，实现数据持久化
- 实体层（Entity）：定义数据模型
- 数据传输层（DTO）：定义数据传输对象
- 通用层（Common）：定义通用工具类和常量

### 后端功能模块
后端已实现的功能模块包括：
- 用户管理模块：实现用户注册、登录、信息管理等功能
- 遥感影像管理模块：实现影像上传、查询、删除等功能
- 分类模型管理模块：实现模型添加、查询、设置默认模型等功能
- 分析任务管理模块：实现任务提交、查询、取消等功能

### 微服务架构
系统采用微服务架构，主要包括以下几个服务：
- 后端服务（web-springboot）：提供核心业务功能和API接口
- 算法服务（web-flask）：提供深度学习模型推理和训练功能
- 文件服务（web-file）：提供文件存储和管理功能

## 技术支持
如有问题请提交Issue或联系技术支持团队。