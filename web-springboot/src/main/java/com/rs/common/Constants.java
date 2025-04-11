package com.rs.common;

/**
 * 系统常量类
 */
public class Constants {

    /**
     * Token请求头名称
     */
    public static final String TOKEN_HEADER = "Authorization";

    /**
     * Redis token前缀
     */
    public static final String REDIS_TOKEN_PREFIX = "token:";

    /**
     * 用户角色
     */
    public static class UserRole {
        /**
         * 管理员
         */
        public static final String ADMIN = "ADMIN";
        
        /**
         * 普通用户
         */
        public static final String USER = "USER";
    }
    
    /**
     * 用户状态
     */
    public static class UserStatus {
        /**
         * 禁用
         */
        public static final int DISABLED = 0;
        
        /**
         * 启用
         */
        public static final int ENABLED = 1;
    }
    
    /**
     * 任务状态
     */
    public static class TaskStatus {
        /**
         * 等待中
         */
        public static final String PENDING = "PENDING";
        
        /**
         * 运行中
         */
        public static final String RUNNING = "RUNNING";
        
        /**
         * 已完成
         */
        public static final String COMPLETED = "COMPLETED";
        
        /**
         * 失败
         */
        public static final String FAILED = "FAILED";
        
        /**
         * 已取消
         */
        public static final String CANCELED = "CANCELED";
    }
    
    /**
     * 操作类型
     */
    public static class OperationType {
        /**
         * 登录
         */
        public static final String LOGIN = "登录";
        
        /**
         * 注销
         */
        public static final String LOGOUT = "注销";
        
        /**
         * 查询
         */
        public static final String QUERY = "查询";
        
        /**
         * 新增
         */
        public static final String INSERT = "新增";
        
        /**
         * 修改
         */
        public static final String UPDATE = "修改";
        
        /**
         * 删除
         */
        public static final String DELETE = "删除";
        
        /**
         * 上传
         */
        public static final String UPLOAD = "上传";
        
        /**
         * 下载
         */
        public static final String DOWNLOAD = "下载";
        
        /**
         * 分析
         */
        public static final String ANALYSIS = "分析";
        
        /**
         * 训练
         */
        public static final String TRAINING = "训练";
    }
    
    /**
     * 操作状态
     */
    public static class OperationStatus {
        /**
         * 失败
         */
        public static final int FAILED = 0;
        
        /**
         * 成功
         */
        public static final int SUCCESS = 1;
    }
}