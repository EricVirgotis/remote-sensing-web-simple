package com.rs.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 操作日志实体类
 */
@Data
@TableName("operation_log")
public class OperationLog {
    
    /**
     * 日志ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;
    
    /**
     * 用户ID
     */
    private Long userId;
    
    /**
     * 操作类型
     */
    private String operation;
    
    /**
     * 请求方法
     */
    private String method;
    
    /**
     * 请求参数
     */
    private String params;
    
    /**
     * IP地址
     */
    private String ip;
    
    /**
     * 操作状态：0-失败，1-成功
     */
    private Integer status;
    
    /**
     * 错误信息
     */
    private String errorMessage;
    
    /**
     * 操作时间
     */
    private LocalDateTime operationTime;
}