package com.rs.utils;

import com.rs.common.Constants;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import jakarta.servlet.http.HttpServletRequest;

/**
 * Token工具类
 */
@Component
public class TokenUtils {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    /**
     * 从请求头中获取token
     *
     * @return token字符串
     */
    public String getTokenFromRequest() {
        ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        if (attributes == null) {
            return null;
        }
        
        HttpServletRequest request = attributes.getRequest();
        String authHeader = request.getHeader(Constants.TOKEN_HEADER);
        
        // 检查Authorization头是否存在且格式正确
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            // 提取token部分
            return authHeader.substring(7);
        }
        
        return null;
    }

    /**
     * 根据token获取用户ID
     *
     * @param token 用户token
     * @return 用户ID
     */
    public Long getUserIdFromToken(String token) {
        if (token == null) {
            return null;
        }
        
        // 从Redis中获取用户ID
        Object userId = redisTemplate.opsForValue().get(Constants.REDIS_TOKEN_PREFIX + token);
        
        // 安全地将Object转换为Long，处理Integer和Long的兼容性
        if (userId != null) {
            if (userId instanceof Integer) {
                return ((Integer) userId).longValue();
            } else if (userId instanceof Long) {
                return (Long) userId;
            } else {
                // 尝试转换其他可能的类型
                try {
                    return Long.valueOf(userId.toString());
                } catch (NumberFormatException e) {
                    return null;
                }
            }
        }
        return null;
    }

    /**
     * 获取当前登录用户ID
     *
     * @return 当前用户ID
     */
    public Long getCurrentUserId() {
        String token = getTokenFromRequest();
        if (token == null || token.trim().isEmpty()) {
            return null;
        }
        Long userId = getUserIdFromToken(token);
        if (userId == null) {
            return null;
        }
        return userId;
    }
}