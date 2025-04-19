package com.rs.utils;

/**
 * 用户上下文工具类
 */
public class UserContext {
    private static final ThreadLocal<Long> USER_ID = new ThreadLocal<>();

    public static Long getUserId() {
        return USER_ID.get();
    }

    public static void setUserId(Long userId) {
        USER_ID.set(userId);
    }

    public static void clear() {
        USER_ID.remove();
    }
}