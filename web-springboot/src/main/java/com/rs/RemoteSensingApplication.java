package com.rs;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.mybatis.spring.annotation.MapperScan;

/**
 * 遥感智能分类分析系统后端服务启动类
 */
@SpringBootApplication
@MapperScan("com.rs.mapper")
public class RemoteSensingApplication {

    public static void main(String[] args) {
        SpringApplication.run(RemoteSensingApplication.class, args);
    }

}