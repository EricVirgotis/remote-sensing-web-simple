package com.rs.config; // 包名根据你的项目结构

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.http.converter.HttpMessageConverter; // 导入 HttpMessageConverter
import org.springframework.http.converter.StringHttpMessageConverter;
// import org.springframework.http.converter.json.MappingJackson2HttpMessageConverter; // 如果需要配置 Jackson，则导入
import org.springframework.web.client.RestTemplate;

import java.nio.charset.StandardCharsets;
import java.util.List; // 导入 List

@Configuration
public class RestTemplateConfig {

    @Bean
    public RestTemplate restTemplate() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(15000); // 15 seconds
        factory.setReadTimeout(15000); // 15 seconds

        RestTemplate restTemplate = new RestTemplate(factory);

        // 获取 RestTemplate 默认的转换器列表
        List<HttpMessageConverter<?>> messageConverters = restTemplate.getMessageConverters();

        // 遍历并修改 StringHttpMessageConverter 的默认编码为 UTF-8
        for (HttpMessageConverter<?> converter : messageConverters) {
            if (converter instanceof StringHttpMessageConverter) {
                ((StringHttpMessageConverter) converter).setDefaultCharset(StandardCharsets.UTF_8);
                // 找到并设置后可以跳出，如果只有一个 StringHttpMessageConverter
                // break;
            }
            // 如果需要对 Jackson 进行特定配置，可以在这里找到并配置
            // if (converter instanceof MappingJackson2HttpMessageConverter) {
            //     MappingJackson2HttpMessageConverter jsonConverter = (MappingJackson2HttpMessageConverter) converter;
            //     // jsonConverter.setObjectMapper(...); // 配置 ObjectMapper
            // }
        }
        // 注意：这里没有调用 setMessageConverters，因为我们是直接修改了列表中的对象引用

        return restTemplate;
    }
}