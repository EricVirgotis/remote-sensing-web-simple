package com.rs.listener;

import com.rs.websocket.TrainingStatusHandler;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.connection.Message;
import org.springframework.data.redis.connection.MessageListener;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.util.Map;

@Component
public class TrainingStatusListener implements MessageListener {

    @Autowired
    private TrainingStatusHandler trainingStatusHandler;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public void onMessage(Message message, byte[] pattern) {
        try {
            // 解析消息内容
            String channel = new String(message.getChannel());
            String messageBody = new String(message.getBody());
            
            // 从channel中提取任务ID
            String taskId = channel.split(":")[1];
            
            // 将消息转换为Map
            Map<String, Object> status = objectMapper.readValue(messageBody, Map.class);
            
            // 通过WebSocket推送给前端
            trainingStatusHandler.sendTrainingStatus(taskId, status);
            
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}