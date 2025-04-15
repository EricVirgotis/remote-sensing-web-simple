package com.example.controller;

import com.example.webspringboot.service.TrainTaskService;
import com.rs.common.Result;
import com.rs.config.TrainServiceConfig; // 导入TrainServiceConfig类
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.rs.entity.TrainTask;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import java.util.HashMap;
import java.util.Map;
import org.springframework.http.HttpEntity;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.core.task.AsyncTaskExecutor;
import org.springframework.beans.factory.annotation.Value;
import com.rs.common.Constants;

@RestController
@RequestMapping("/train-task")
public class TrainTaskController {
    private final TrainTaskService trainTaskService;
    
    private static final Logger log = LoggerFactory.getLogger(TrainTaskController.class);
    
    private void updateTaskStatus(Long taskId, Integer status) {
        try {
            TrainTask task = new TrainTask();
            task.setId(taskId);
            task.setTaskStatus(status);
            trainTaskService.updateById(task);
        } catch (Exception e) {
            log.error("更新任务状态失败: {}", e.getMessage());
        }
    }
    
    @Autowired
    private RestTemplate restTemplate;
    
    @Autowired
    private AsyncTaskExecutor asyncTaskExecutor;
    
    @Autowired
    private TrainServiceConfig trainServiceConfig;
    
    @Autowired
    private com.rs.mapper.TrainingDatasetMapper trainingDatasetMapper;

    public TrainTaskController(TrainTaskService trainTaskService) {
        this.trainTaskService = trainTaskService;
    }
    
    @Async
    public void asyncSubmitTrainTask(Long taskId, HttpEntity<Map<String, Object>> requestEntity, Map<String, Object> requestMap) {
        // 重试次数和间隔配置
        int maxRetries = trainServiceConfig.getRetry().getMaxAttempts();
        long retryIntervalMs = trainServiceConfig.getRetry().getIntervalMs();
        int retryCount = 0;
        
        while (retryCount < maxRetries) {
            try {
                log.info("提交训练任务到训练服务，任务ID: {}, 尝试次数: {}", taskId, retryCount + 1);
                String trainingUrl = trainServiceConfig.getTrainingUrl(); // 使用正确的Flask端点路径
                log.info("提交训练任务到训练服务 URL: {}", trainingUrl);
                ResponseEntity<String> response = restTemplate.postForEntity(trainingUrl, requestEntity, String.class);
                
                if (response.getStatusCode().is2xxSuccessful()) {
                    log.info("训练任务提交成功，任务ID: {}", taskId);
                    updateTaskStatus(taskId, Constants.TrainTaskStatus.IN_PROGRESS);
                    return; // 成功提交，退出重试循环
                } else {
                    log.error("训练服务返回错误状态码: {}, 任务ID: {}", response.getStatusCode(), taskId);
                    if (retryCount < maxRetries - 1) {
                        retryCount++;
                        log.info("将在{}毫秒后重试提交训练任务，任务ID: {}", retryIntervalMs, taskId);
                        Thread.sleep(retryIntervalMs);
                        continue;
                    }
                    updateTaskStatus(taskId, Constants.TrainTaskStatus.SUBMIT_FAILED);
                    return;
                }
            } catch (HttpClientErrorException e) {
                log.error("训练任务提交失败，任务ID: {}, URL: {}, 错误: {}", taskId, trainServiceConfig.getUrl(), e.getMessage());
                log.error("请求参数: {}", requestMap);
                log.error("响应状态码: {}", e.getStatusCode());
                log.error("错误详情: {}", e.getResponseBodyAsString());
                
                if (e.getStatusCode() == HttpStatus.NOT_FOUND) {
                    updateTaskStatus(taskId, Constants.TrainTaskStatus.ENDPOINT_NOT_FOUND);
                    return; // 端点不存在，不重试
                } else if (retryCount < maxRetries - 1) {
                    retryCount++;
                    try {
                        log.info("将在{}毫秒后重试提交训练任务，任务ID: {}", retryIntervalMs, taskId);
                        Thread.sleep(retryIntervalMs);
                        continue;
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        log.error("重试等待被中断", ie);
                    }
                }
                updateTaskStatus(taskId, Constants.TrainTaskStatus.OTHER_ERROR);
                return;
            } catch (ResourceAccessException e) {
                log.error("训练服务连接失败，任务ID: {}, URL: {}, 错误: {}", taskId, trainServiceConfig.getUrl(), e.getMessage());
                log.error("请求参数: {}", requestMap);
                
                if (retryCount < maxRetries - 1) {
                    retryCount++;
                    try {
                        log.info("将在{}毫秒后重试提交训练任务，任务ID: {}", retryIntervalMs, taskId);
                        Thread.sleep(retryIntervalMs);
                        continue;
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        log.error("重试等待被中断", ie);
                    }
                }
                updateTaskStatus(taskId, Constants.TrainTaskStatus.NETWORK_ERROR);
                return;
            } catch (Exception e) {
                log.error("训练任务提交失败，任务ID: {}, URL: {}, 错误: {}", taskId, trainServiceConfig.getUrl(), e.getMessage());
                log.error("请求参数: {}", requestMap);
                
                if (retryCount < maxRetries - 1) {
                    retryCount++;
                    try {
                        log.info("将在{}毫秒后重试提交训练任务，任务ID: {}", retryIntervalMs, taskId);
                        Thread.sleep(retryIntervalMs);
                        continue;
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        log.error("重试等待被中断", ie);
                    }
                }
                updateTaskStatus(taskId, Constants.TrainTaskStatus.OTHER_ERROR);
                return;
            }
        }
    }

    @Autowired
    private com.rs.utils.TokenUtils tokenUtils;

    @PostMapping("/create")
    public Result<String> createTrainTask(@RequestBody TrainTask trainTask) {
        try {
            // 设置必要的字段值
            // 前端传入的name字段映射到taskName
            if (trainTask.getTaskName() == null && trainTask.getName() != null) {
                trainTask.setTaskName(trainTask.getName());
            }
            
            // 前端传入的modelName字段映射到modelType和model_name
            if (trainTask.getModelName() != null) {
                // 确保modelType有值
                if (trainTask.getModelType() == null) {
                    trainTask.setModelType(trainTask.getModelName());
                }
                // model_name字段已通过@TableField注解映射，无需额外处理
            }
            
            // 从SecurityContext获取当前用户ID
            Long userId = tokenUtils.getCurrentUserId();
            if (userId == null) {
                return Result.error(401, "用户未认证");
            }
            trainTask.setUserId(userId);
            
            // 设置初始任务状态为进行中(0)
            if (trainTask.getTaskStatus() == null) {
                trainTask.setTaskStatus(Constants.TrainTaskStatus.IN_PROGRESS);
            }
            
            // 将训练参数转换为JSON格式存储
            try {
                com.alibaba.fastjson.JSONObject paramsJson = new com.alibaba.fastjson.JSONObject();
                paramsJson.put("epochs", trainTask.getEpochs());
                paramsJson.put("batchSize", trainTask.getBatchSize());
                paramsJson.put("learningRate", trainTask.getLearningRate());
                paramsJson.put("usePretrained", trainTask.getUsePretrained());
                trainTask.setParameters(paramsJson.toJSONString());
            } catch (Exception e) {
                System.err.println("参数转换失败: " + e.getMessage());
            }
            
            trainTaskService.save(trainTask);
            
            // 异步提交到训练服务
            try {
                // 先检查训练服务是否可用，添加重试机制
                int maxHealthRetries = trainServiceConfig.getHealthCheck().getMaxAttempts();
                long healthRetryIntervalMs = trainServiceConfig.getHealthCheck().getIntervalMs();
                int healthRetryCount = 0;
                Exception lastException = null;
                
                while (healthRetryCount <= maxHealthRetries) {
                    try {
                        log.info("检查训练服务健康状态，尝试次数: {}", healthRetryCount + 1);
                        String healthCheckUrl = trainServiceConfig.getUrl() + "/api/train/health";
                        ResponseEntity<String> healthCheck = restTemplate.getForEntity(healthCheckUrl, String.class);
                        
                        if (healthCheck.getStatusCode().is2xxSuccessful()) {
                            log.info("训练服务健康检查成功");
                            break; // 健康检查成功，继续后续操作
                        } else {
                            log.warn("训练服务健康检查返回非成功状态码: {}", healthCheck.getStatusCode());
                            if (healthRetryCount < maxHealthRetries) {
                                healthRetryCount++;
                                log.info("将在{}毫秒后重试健康检查", healthRetryIntervalMs);
                                Thread.sleep(healthRetryIntervalMs);
                                continue;
                            }
                            log.error("训练服务健康检查失败，已达到最大重试次数: {}", healthCheck.getStatusCode());
                            updateTaskStatus(trainTask.getId(), Constants.TrainTaskStatus.SUBMIT_FAILED);
                            return Result.error(healthCheck.getStatusCode().value(), "训练服务健康检查失败: " + healthCheck.getStatusCode() + "，请确认训练服务是否正常运行");
                        }
                    } catch (Exception e) {
                        lastException = e;
                        log.warn("训练服务健康检查异常: {}", e.getMessage());
                        if (healthRetryCount < maxHealthRetries) {
                            healthRetryCount++;
                            try {
                                log.info("将在{}毫秒后重试健康检查", healthRetryIntervalMs);
                                Thread.sleep(healthRetryIntervalMs);
                                continue;
                            } catch (InterruptedException ie) {
                                Thread.currentThread().interrupt();
                                log.error("健康检查重试等待被中断", ie);
                            }
                        } else {
                            log.error("训练服务健康检查失败，已达到最大重试次数，错误: {}", e.getMessage());
                            updateTaskStatus(trainTask.getId(), Constants.TrainTaskStatus.NETWORK_ERROR);
                            return Result.error(500, "训练服务不可用，请检查训练服务是否已启动: " + e.getMessage());
                        }
                    }
                }
                
                // 如果所有重试都失败了
                if (healthRetryCount > maxHealthRetries && lastException != null) {
                    log.error("训练服务健康检查失败，已达到最大重试次数，错误: {}", lastException.getMessage());
                    updateTaskStatus(trainTask.getId(), Constants.TrainTaskStatus.NETWORK_ERROR);
                    return Result.error(500, "训练服务不可用，请检查训练服务是否已启动: " + lastException.getMessage());
                }
                
                // 调用算法服务进行训练
                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.valueOf("application/json;charset=UTF-8"));
                
                Map<String, Object> requestMap = new HashMap<>();
                // 获取数据集名称
                com.rs.entity.TrainingDataset dataset = trainingDatasetMapper.selectById(trainTask.getDatasetId());
                if (dataset == null) {
                    log.error("数据集不存在，ID: {}", trainTask.getDatasetId());
                    updateTaskStatus(trainTask.getId(), Constants.TrainTaskStatus.SUBMIT_FAILED);
                    return Result.error(400, "数据集不存在");
                }
                
                requestMap.put("task_name", trainTask.getTaskName());
                requestMap.put("dataset_name", dataset.getDatasetName());
                requestMap.put("model_name", trainTask.getModelName());
                
                // 解析parameters字符串为JSON对象
                com.alibaba.fastjson.JSONObject params = com.alibaba.fastjson.JSON.parseObject(trainTask.getParameters());
                requestMap.put("epochs", params.getInteger("epochs"));
                requestMap.put("batch_size", params.getInteger("batchSize"));
                requestMap.put("learning_rate", params.getDouble("learningRate"));
                
                HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestMap, headers);
                
                // 异步调用
                asyncSubmitTrainTask(trainTask.getId(), requestEntity, requestMap);
                
                return Result.success("训练任务已创建，正在后台提交...");
            } catch (Exception e) {
                log.error("训练任务提交异常: {}", e.getMessage());
                return Result.error(500, "训练任务创建成功，但提交到训练服务失败：" + e.getMessage());
            }
        } catch (Exception e) {
            e.printStackTrace(); // 打印完整堆栈信息到日志
            return Result.error(500, "创建训练任务失败: " + e.getMessage());
        }
    }

    @GetMapping("/{id:\\d+}")
    public Result<TrainTask> getTrainTaskById(@PathVariable Long id) {
        try {
            TrainTask trainTask = trainTaskService.getById(id);
            if (trainTask == null) {
                return Result.error(404, "未找到该训练任务");
            }
            return Result.success(trainTask);
        } catch (Exception e) {
            return Result.error(500, "获取训练任务详情失败: " + e.getMessage());
        }
    }

    @GetMapping("/page")
    public Result<Page<TrainTask>> pageTrainTasks(
        @RequestParam(defaultValue = "1") Integer current,
        @RequestParam(defaultValue = "10") Integer size,
        @RequestParam(required = false) String name,
        @RequestParam(required = false) Integer status,
        @RequestParam(required = false) String model_name
    ) {
        try {
            Page<TrainTask> page = new Page<>(current, size);
            Page<TrainTask> result = trainTaskService.pageTrainTasks(page, name, status, model_name);
            return Result.success(result != null ? result : page);
        } catch (Exception e) {
            return Result.error(500, "查询训练任务列表失败: " + e.getMessage());
        }
    }

    @DeleteMapping("/{id}")
    public Result<String> deleteTrainTask(@PathVariable Long id) {
        try {
            // 先删除数据库记录
            boolean removed = trainTaskService.removeById(id);
            if (!removed) {
                return Result.error(404, "未找到该训练任务");
            }
            return Result.success("训练任务删除成功");
        } catch (Exception e) {
            return Result.error(500, "删除训练任务失败: " + e.getMessage());
        }
    }
}