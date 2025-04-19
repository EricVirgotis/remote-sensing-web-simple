package com.rs.filter;

import com.rs.utils.TokenUtils;
import com.rs.utils.UserContext;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Collections;

public class JwtAuthenticationFilter extends OncePerRequestFilter {

    @Autowired
    private TokenUtils tokenUtils;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        
        try {
            String token = tokenUtils.getTokenFromRequest();
            if (token != null) {
                Long userId = tokenUtils.getUserIdFromToken(token);
                if (userId != null) {
                    // 创建认证对象
                    UsernamePasswordAuthenticationToken authentication = new UsernamePasswordAuthenticationToken(
                        userId,
                        null,
                        Collections.singletonList(new SimpleGrantedAuthority("ROLE_USER"))
                    );
                    
                    // 设置认证信息到上下文
                    SecurityContextHolder.getContext().setAuthentication(authentication);
                    // 设置用户ID到UserContext
                    UserContext.setUserId(userId);
                }
            }
        } catch (Exception e) {
            logger.error("无法设置用户认证信息", e);
        }

        filterChain.doFilter(request, response);
    }
}