-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS rs_analysis DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE rs_analysis;

-- 用户表
CREATE TABLE IF NOT EXISTS `user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `password` varchar(100) NOT NULL COMMENT '密码',
  `real_name` varchar(50) DEFAULT NULL COMMENT '真实姓名',
  `email` varchar(100) DEFAULT NULL COMMENT '邮箱',
  `phone` varchar(20) DEFAULT NULL COMMENT '手机号',
  `avatar` varchar(255) DEFAULT NULL COMMENT '头像URL',
  `role` varchar(20) NOT NULL DEFAULT 'USER' COMMENT '角色：ADMIN-管理员，USER-普通用户',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 遥感影像表
CREATE TABLE IF NOT EXISTS `remote_image` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '影像ID',
  `user_id` bigint(20) NOT NULL COMMENT '用户ID',
  `image_name` varchar(100) NOT NULL COMMENT '影像名称',
  `image_path` varchar(255) NOT NULL COMMENT '影像存储路径',
  `image_size` bigint(20) NOT NULL COMMENT '影像大小(字节)',
  `image_format` varchar(20) NOT NULL COMMENT '影像格式',
  `upload_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  `description` varchar(500) DEFAULT NULL COMMENT '影像描述',
  `metadata` text DEFAULT NULL COMMENT '元数据JSON',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态：0-无效，1-有效',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='遥感影像表';

-- 分类模型表
CREATE TABLE IF NOT EXISTS `classification_model` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '模型ID',
  `user_id` bigint(20) NOT NULL COMMENT '用户ID（系统提供的模型的用户ID是管理员ID——1）',
  `model_name` varchar(100) NOT NULL COMMENT '模型名称',
  `model_path` varchar(255) NOT NULL COMMENT '模型存储路径',
  `model_type` varchar(50) NOT NULL COMMENT '模型类型',
  `description` varchar(500) DEFAULT NULL COMMENT '模型描述',
  `accuracy` decimal(5,2) DEFAULT NULL COMMENT '模型精度',
  `parameters` text DEFAULT NULL COMMENT '模型参数JSON',
  `is_default` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否默认模型（系统提供的已训练好的模型，可以直接拿来用，不需要自己去训练才能用）：0-否，1-是',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分类模型表';

-- 分析任务表
CREATE TABLE IF NOT EXISTS `analysis_task` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '任务ID',
  `user_id` bigint(20) NOT NULL COMMENT '用户ID',
  `image_id` bigint(20) NOT NULL COMMENT '影像ID',
  `model_id` bigint(20) NOT NULL COMMENT '模型ID',
  `task_name` varchar(100) NOT NULL COMMENT '任务名称',
  `task_status` varchar(20) NOT NULL COMMENT '任务状态：PENDING-等待中，RUNNING-运行中，COMPLETED-已完成，FAILED-失败',
  `result_path` varchar(255) DEFAULT NULL COMMENT '结果存储路径',
  `start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `error_message` varchar(500) DEFAULT NULL COMMENT '错误信息',
  `parameters` text DEFAULT NULL COMMENT '任务参数JSON',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_image_id` (`image_id`),
  KEY `idx_model_id` (`model_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析任务表';

-- 训练数据集表
CREATE TABLE IF NOT EXISTS `training_dataset` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '数据集ID',
  `user_id` bigint(20) NOT NULL COMMENT '用户ID',
  `dataset_name` varchar(100) NOT NULL COMMENT '数据集名称',
  `dataset_path` varchar(255) NOT NULL COMMENT '数据集存储路径',
  `dataset_size` bigint(20) NOT NULL COMMENT '数据集大小(字节)',
  `sample_count` int(11) DEFAULT NULL COMMENT '样本数量',
  `description` varchar(500) DEFAULT NULL COMMENT '数据集描述',
  `metadata` text DEFAULT NULL COMMENT '元数据JSON',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态：0-无效，1-有效',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='训练数据集表';

-- 模型训练任务表
CREATE TABLE IF NOT EXISTS `training_task` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '训练任务ID',
  `user_id` bigint(20) NOT NULL COMMENT '用户ID',
  `dataset_id` bigint(20) NOT NULL COMMENT '数据集ID',
  `task_name` varchar(100) NOT NULL COMMENT '任务名称',
  `model_name` varchar(100) NOT NULL COMMENT '模型名称',
  `model_type` varchar(50) NOT NULL COMMENT '模型类型',
  `task_status` varchar(20) NOT NULL COMMENT '任务状态：PENDING-等待中，RUNNING-运行中，COMPLETED-已完成，FAILED-失败',
  `progress` int DEFAULT 0 COMMENT '训练进度(0-100)',
  `model_path` varchar(255) DEFAULT NULL COMMENT '生成模型存储路径',
  `start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `accuracy` decimal(5,2) DEFAULT NULL COMMENT '模型精度',
  `loss` decimal(10,4) DEFAULT NULL COMMENT '损失值',
  `parameters` text DEFAULT NULL COMMENT '训练参数JSON',
  `error_message` varchar(500) DEFAULT NULL COMMENT '错误信息',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_dataset_id` (`dataset_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='模型训练任务表';

-- 操作日志表
CREATE TABLE IF NOT EXISTS `operation_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '日志ID',
  `user_id` bigint(20) DEFAULT NULL COMMENT '用户ID',
  `operation` varchar(50) NOT NULL COMMENT '操作类型',
  `method` varchar(100) NOT NULL COMMENT '请求方法',
  `params` text DEFAULT NULL COMMENT '请求参数',
  `ip` varchar(50) DEFAULT NULL COMMENT 'IP地址',
  `status` tinyint(1) NOT NULL COMMENT '操作状态：0-失败，1-成功',
  `error_message` varchar(500) DEFAULT NULL COMMENT '错误信息',
  `operation_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_operation_time` (`operation_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';

-- 插入初始管理员账号
INSERT IGNORE INTO `user` (`username`, `password`, `real_name`, `email`, `role`, `status`) VALUES
('admin', '$2a$10$ySG2lkvjFHY5O0./CPIE1OI8VJsuKYEzOYzqIa7AJR6sEgSzUFOAm', '系统管理员', 'admin@example.com', 'ADMIN', 1);

-- 插入预训练的默认模型 (关联管理员用户ID=1)
-- 添加唯一性约束，防止重复插入预训练模型
ALTER TABLE `classification_model` ADD UNIQUE INDEX `uk_model_name_type` (`model_name`, `model_type`) WHERE `deleted` = 0;
ALTER TABLE `classification_model` ADD UNIQUE INDEX `uk_model_path` (`model_path`) WHERE `deleted` = 0;

-- 使用IGNORE关键字插入预训练模型，避免重复插入
INSERT IGNORE INTO `classification_model` (`user_id`, `model_name`, `model_path`, `model_type`, `description`, `accuracy`, `is_default`, `status`, `deleted`) VALUES
(1, 'AlexNet', 'D:/Code/System/remote-sensing-web-simple/remote-sensing-web-simple3/remote-sensing-web-simple/web-flask/models/AlexNet.h5', 'CNN', '预训练的 AlexNet 模型', 0.80, 1, 1, 0),
(1, 'GoogLeNet', 'D:/Code/System/remote-sensing-web-simple/remote-sensing-web-simple3/remote-sensing-web-simple/web-flask/models/GoogLeNet.h5', 'CNN', '预训练的 GoogLeNet 模型', 0.84, 1, 1, 0),
(1, 'ResNet50', 'D:/Code/System/remote-sensing-web-simple/remote-sensing-web-simple3/remote-sensing-web-simple/web-flask/models/ResNet50.h5', 'CNN', '预训练的 ResNet50 模型', 0.96, 1, 1, 0),
(1, 'VGGNet-16', 'D:/Code/System/remote-sensing-web-simple/remote-sensing-web-simple3/remote-sensing-web-simple/web-flask/models/VGGNet-16.h5', 'CNN', '预训练的 VGGNet-16 模型', 0.76, 1, 1, 0);

-- 在模型训练完成后插入模型数据到分类模型表
-- 注意：以下语句需要在应用程序中动态替换变量值后执行
INSERT INTO `classification_model` (`user_id`, `model_name`, `model_path`, `model_type`, `description`, `accuracy`, `parameters`, `is_default`, `status`) 
SELECT 
  `user_id`,
  `model_name`, 
  `model_path`, 
  `model_type`, 
  CONCAT('由训练任务 "', `task_name`, '" 生成的模型'), 
  `accuracy`, 
  `parameters`, 
  0, -- 非默认模型
  1  -- 启用状态
FROM `training_task` 
WHERE `task_status` = 'COMPLETED' AND `id` = ?; -- 需要替换为实际的训练任务ID