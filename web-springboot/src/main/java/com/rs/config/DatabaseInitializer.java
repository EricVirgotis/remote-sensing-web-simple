package com.rs.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.io.ClassPathResource;
import org.springframework.jdbc.datasource.init.ResourceDatabasePopulator;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;

/**
 * 数据库初始化器
 * 在应用启动时自动执行数据库初始化脚本
 */
@Component
public class DatabaseInitializer implements CommandLineRunner {

    private static final Logger logger = LoggerFactory.getLogger(DatabaseInitializer.class);

    @Autowired
    private DataSource dataSource;

    @Value("${spring.datasource.url}")
    private String datasourceUrl;
    
    @Value("${spring.datasource.username}")
    private String datasourceUsername;
    
    @Value("${spring.datasource.password}")
    private String datasourcePassword;

    @Override
    public void run(String... args) {
        logger.info("开始初始化数据库...");
        
        // 首先确保数据库存在
        ensureDatabaseExists();
        
        // 执行初始化SQL脚本
        executeInitScript();
        
        logger.info("数据库初始化完成");
    }

    /**
     * 确保数据库存在，如果不存在则创建
     */
    private void ensureDatabaseExists() {
        // 从JDBC URL中提取数据库名称
        String dbName = extractDatabaseName(datasourceUrl);
        if (dbName == null || dbName.isEmpty()) {
            logger.warn("无法从JDBC URL中提取数据库名称");
            return;
        }
        
        logger.info("尝试创建数据库: {}", dbName);
        
        try (Connection conn = dataSource.getConnection()) {
            try (Statement stmt = conn.createStatement()) {
                // 创建数据库的SQL语句，确保只使用纯数据库名称
                String createDbSql = "CREATE DATABASE IF NOT EXISTS " + dbName;
                logger.info("执行SQL: {}", createDbSql);
                stmt.executeUpdate(createDbSql);
                logger.info("数据库创建成功或已存在: {}", dbName);
            }
        } catch (SQLException e) {
            logger.error("创建数据库时发生错误", e);
        }
    }

    /**
     * 执行初始化SQL脚本
     */
    private void executeInitScript() {
        try {
            ResourceDatabasePopulator populator = new ResourceDatabasePopulator();
            populator.addScript(new ClassPathResource("db/init.sql"));
            populator.execute(dataSource);
            logger.info("成功执行数据库初始化脚本");
        } catch (Exception e) {
            logger.error("执行数据库初始化脚本时发生错误", e);
        }
    }

    /**
     * 从JDBC URL中提取数据库名称
     */
    private String extractDatabaseName(String jdbcUrl) {
        // 假设URL格式为：jdbc:mysql://localhost:3306/dbname?param=value
        try {
            // 查找主机部分之后的第一个斜杠
            int hostStartIndex = jdbcUrl.indexOf("//");
            if (hostStartIndex == -1) {
                logger.warn("JDBC URL格式不正确，缺少主机部分: {}", jdbcUrl);
                return null;
            }
            
            // 找到主机部分之后的第一个斜杠，这个斜杠后面应该是数据库名称
            int dbNameStartIndex = jdbcUrl.indexOf("/", hostStartIndex + 2);
            if (dbNameStartIndex == -1) {
                logger.warn("JDBC URL格式不正确，缺少数据库名称: {}", jdbcUrl);
                return null;
            }
            
            // 提取数据库名称，直到问号（如果有的话）
            String dbNameWithParams = jdbcUrl.substring(dbNameStartIndex + 1);
            int questionMarkIndex = dbNameWithParams.indexOf("?");
            
            if (questionMarkIndex == -1) {
                // 如果没有问号，检查是否有其他参数分隔符
                int ampersandIndex = dbNameWithParams.indexOf("&");
                if (ampersandIndex != -1) {
                    logger.warn("URL格式异常，包含&但没有?: {}", jdbcUrl);
                    return dbNameWithParams.substring(0, ampersandIndex);
                }
                return dbNameWithParams;
            } else {
                return dbNameWithParams.substring(0, questionMarkIndex);
            }
        } catch (Exception e) {
            logger.error("从JDBC URL提取数据库名称时发生错误: {}", jdbcUrl, e);
            return null;
        }
    }
}