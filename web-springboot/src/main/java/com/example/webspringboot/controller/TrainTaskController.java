package com.example.webspringboot.controller;

import com.example.webspringboot.service.TrainTaskService;
import com.rs.common.Result;
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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestController
@RequestMapping("/train-task")
public class TrainTaskController {
    private final TrainTaskService trainTaskService;
    
    private static final Logger log = LoggerFactory.getLogger(TrainTaskController.class);
    
    @Autowired
    private RestTemplate restTemplate;

    public TrainTaskController(TrainTaskService trainTaskService) {
        this.trainTaskService = trainTaskService;
    }

    @PostMapping
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
            
            // 设置默认的用户ID（实际应用中应从登录用户获取）
            if (trainTask.getUserId() == null) {
                trainTask.setUserId(1L); // 默认用户ID
            }
            
            // 设置初始任务状态为进行中(0)
            if (trainTask.getTaskStatus() == null) {
                trainTask.setTaskStatus(0);
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
                // 调用算法服务进行训练
                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_JSON);
                
                Map<String, Object> requestMap = new HashMap<>();
                requestMap.put("taskId", trainTask.getId());
                requestMap.put("datasetId", trainTask.getDatasetId());
                requestMap.put("modelName", trainTask.getModelName());
                requestMap.put("parameters", trainTask.getParameters());
                
                HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestMap, headers);
                
                // 异步调用
                new Thread(() -> {
                    try {
                        restTemplate.postForEntity("http://localhost:5000/train", requestEntity, String.class);
                    } catch (Exception e) {
                        log.error("训练任务提交失败: {}", e.getMessage());
                    }
                }).start();
                
                return Result.success("训练任务创建并已提交训练");
            } catch (Exception e) {
                log.error("训练任务提交异常: {}", e.getMessage());
                return Result.success("训练任务创建成功，但提交训练失败");
            }
        } catch (Exception e) {
            e.printStackTrace(); // 打印完整堆栈信息到日志
            return Result.error(500, "创建训练任务失败: " + e.getMessage());
        }
    }

    @GetMapping("/{id}")
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