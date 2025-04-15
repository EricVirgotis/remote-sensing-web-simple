package com.rs.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "train.service")
public class TrainServiceConfig {
    @Value("${train.api.path}")
    private String trainingPath;

    public String getTrainingUrl() {
        return url + trainingPath;
    }
    private String url;
    private RetryConfig retry;
    private HealthCheckConfig healthCheck;

    public static class RetryConfig {
        private int maxAttempts;
        private long intervalMs;

        // Getters and Setters
        public int getMaxAttempts() { return maxAttempts; }
        public void setMaxAttempts(int maxAttempts) { this.maxAttempts = maxAttempts; }
        public long getIntervalMs() { return intervalMs; }
        public void setIntervalMs(long intervalMs) { this.intervalMs = intervalMs; }
    }

    public static class HealthCheckConfig {
        private int maxAttempts;
        private long intervalMs;
        private String path;

        // Getters and Setters
        public int getMaxAttempts() { return maxAttempts; }
        public void setMaxAttempts(int maxAttempts) { this.maxAttempts = maxAttempts; }
        public long getIntervalMs() { return intervalMs; }
        public void setIntervalMs(long intervalMs) { this.intervalMs = intervalMs; }
        public String getPath() { return path; }
        public void setPath(String path) { this.path = path; }
    }



    // Getters and Setters
    public String getUrl() { return url; }
    public void setUrl(String url) { this.url = url; }
    public RetryConfig getRetry() { return retry; }
    public void setRetry(RetryConfig retry) { this.retry = retry; }
    public HealthCheckConfig getHealthCheck() { return healthCheck; }
    public void setHealthCheck(HealthCheckConfig healthCheck) { this.healthCheck = healthCheck; }
}