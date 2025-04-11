package com.rs.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.boot.CommandLineRunner;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.StringRedisSerializer;
import java.io.IOException;

@Configuration
public class RedisConfig implements CommandLineRunner {
    
    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory redisConnectionFactory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(redisConnectionFactory);
        
        // 使用StringRedisSerializer来序列化和反序列化redis的key值
        template.setKeySerializer(new StringRedisSerializer());
        
        // 使用GenericJackson2JsonRedisSerializer来序列化和反序列化redis的value值
        template.setValueSerializer(new GenericJackson2JsonRedisSerializer());
        
        template.setHashKeySerializer(new StringRedisSerializer());
        template.setHashValueSerializer(new GenericJackson2JsonRedisSerializer());
        
        template.afterPropertiesSet();
        return template;
    }

    @Override
    public void run(String... args) throws Exception {
        try {
            ProcessBuilder builder = new ProcessBuilder("D:\\Code\\System\\remote-sensing-web-simple\\remote-sensing-web-simple\\web-springboot\\src\\main\\java\\com\\rs\\config\\Redis\\redis-server.exe");
            builder.redirectErrorStream(true);
            Process process = builder.start();
            System.out.println("Redis服务已启动，进程ID: " + process.pid());
        } catch (IOException e) {
            System.err.println("Redis服务启动失败: " + e.getMessage());
        }
    }
}