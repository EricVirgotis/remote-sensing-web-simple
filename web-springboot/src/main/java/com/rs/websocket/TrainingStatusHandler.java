package com.rs.websocket;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class TrainingStatusHandler extends TextWebSocketHandler {

    private final Map<String, WebSocketSession> sessions = new ConcurrentHashMap<>();
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        String sessionId = session.getId();
        sessions.put(sessionId, session);
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) {
        // 处理客户端消息，如订阅特定任务的状态更新
        try {
            Map<String, Object> payload = objectMapper.readValue(message.getPayload(), Map.class);
            String taskId = (String) payload.get("taskId");
            if (taskId != null) {
                // 将会话ID与任务ID关联存储在Redis中
                redisTemplate.opsForSet().add("training_task:" + taskId + ":subscribers", session.getId());
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        String sessionId = session.getId();
        sessions.remove(sessionId);
    }

    public void sendTrainingStatus(String taskId, Map<String, Object> status) {
        try {
            String message = objectMapper.writeValueAsString(status);
            // 获取订阅该任务的所有会话ID
            var subscriberIds = redisTemplate.opsForSet().members("training_task:" + taskId + ":subscribers");
            if (subscriberIds != null) {
                for (Object sessionId : subscriberIds) {
                    WebSocketSession session = sessions.get(sessionId.toString());
                    if (session != null && session.isOpen()) {
                        session.sendMessage(new TextMessage(message));
                    }
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}