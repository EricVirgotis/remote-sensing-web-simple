package com.rs.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ClassPathResource;
import org.springframework.jdbc.datasource.init.ResourceDatabasePopulator;

import jakarta.annotation.PostConstruct;
import javax.sql.DataSource;

/**
 * 嵌入式数据库配置
 * 用于在应用启动时自动初始化和启动数据库
 */
@Configuration
public class EmbeddedDatabaseConfig {

    private static final Logger logger = LoggerFactory.getLogger(EmbeddedDatabaseConfig.class);

    @Value("${spring.datasource.url}")
    private String datasourceUrl;

    @Value("${spring.datasource.username}")
    private String datasourceUsername;

    @Value("${spring.datasource.password}")
    private String datasourcePassword;

    @PostConstruct
    public void init() {
        logger.info("数据库配置初始化，URL: {}", datasourceUrl);
    }

    /**
     * 初始化数据库
     * 执行SQL脚本创建表和初始数据
     */
    @Bean
    public ResourceDatabasePopulator databasePopulator(DataSource dataSource) {
        logger.info("开始初始化数据库...");
        ResourceDatabasePopulator populator = new ResourceDatabasePopulator();
        populator.addScript(new ClassPathResource("db/init.sql"));
        
        try {
            populator.execute(dataSource);
            logger.info("数据库初始化完成");
        } catch (Exception e) {
            logger.error("执行数据库初始化脚本时发生错误", e);
        }
        
        return populator;
    }
}