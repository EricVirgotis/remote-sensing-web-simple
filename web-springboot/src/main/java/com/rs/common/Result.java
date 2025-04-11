package com.rs.common;

import lombok.Data;

import java.io.Serializable;

/**
 * 统一响应结果类
 */
@Data
public class Result<T> implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 状态码
     */
    private Integer code;

    /**
     * 消息
     */
    private String message;

    /**
     * 数据
     */
    private T data;

    /**
     * 是否成功
     */
    private Boolean success;

    /**
     * 私有构造方法
     */
    private Result() {
    }

    /**
     * 成功返回结果
     *
     * @param <T> 数据类型
     * @return 结果
     */
    public static <T> Result<T> success() {
        return success(null);
    }

    /**
     * 成功返回结果
     *
     * @param data 数据
     * @param <T>  数据类型
     * @return 结果
     */
    public static <T> Result<T> success(T data) {
        return success("操作成功", data);
    }

    /**
     * 成功返回结果
     *
     * @param message 消息
     * @param data    数据
     * @param <T>     数据类型
     * @return 结果
     */
    public static <T> Result<T> success(String message, T data) {
        Result<T> result = new Result<>();
        result.setCode(200);
        result.setMessage(message);
        result.setData(data);
        result.setSuccess(true);
        return result;
    }

    /**
     * 失败返回结果
     *
     * @param <T> 数据类型
     * @return 结果
     */
    public static <T> Result<T> error() {
        return error("操作失败");
    }

    /**
     * 失败返回结果
     *
     * @param message 消息
     * @param <T>     数据类型
     * @return 结果
     */
    public static <T> Result<T> error(String message) {
        return error(500, message);
    }

    /**
     * 失败返回结果
     *
     * @param code    状态码
     * @param message 消息
     * @param <T>     数据类型
     * @return 结果
     */
    public static <T> Result<T> error(Integer code, String message) {
        Result<T> result = new Result<>();
        result.setCode(code);
        result.setMessage(message);
        result.setData(null);
        result.setSuccess(false);
        return result;
    }
}