package com.example.webspringboot.controller;

import com.example.webspringboot.service.TrainTaskService;
import com.rs.common.Result;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.rs.entity.TrainingDataset;     // 导入 Dataset 实体
import com.rs.mapper.TrainingDatasetMapper; // 导入 Mapper
import com.rs.entity.TrainTask;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import java.util.HashMap;
import java.util.Map;
import org.springframework.http.HttpEntity;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestController
@RequestMapping("/train-task")
public class TrainTaskController {
    private final TrainTaskService trainTaskService;
    
    private static final Logger log = LoggerFactory.getLogger(TrainTaskController.class);

    @Value("${rs.algorithm.url}") // 从配置文件注入算法服务的基础 URL
    private String algorithmServiceUrl;
    
    @Autowired
    private RestTemplate restTemplate;
    @Autowired
    private com.rs.utils.TokenUtils tokenUtils;
    @Autowired
    private TrainingDatasetMapper trainingDatasetMapper; // 注入 Dataset Mapper

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
                Long userId = tokenUtils.getCurrentUserId();
                if (userId == null) {
                    return Result.error(401, "未登录或登录已过期");
                }
                trainTask.setUserId(userId);
            }
            
            // 设置初始任务状态为进行中(PENDING)
            if (trainTask.getTaskStatus() == null) {
                trainTask.setTaskStatus("PENDING");
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
                // 新增代码：查询数据集名称
                TrainingDataset dataset = trainingDatasetMapper.selectById(trainTask.getDatasetId());
                if (dataset == null) {
                    log.error("无法找到 ID 为 {} 的数据集，无法提交训练任务 {}", trainTask.getDatasetId(), trainTask.getId());
                    // 根据你的业务逻辑，这里可以选择是仅记录错误、更新任务状态为失败，还是返回一个特定的错误信息
                    // 这里暂时先返回创建成功但提交失败
                    return Result.success("训练任务创建成功，但提交训练失败：未找到对应数据集");
                }
                String datasetName = dataset.getDatasetName(); // 获取数据集名称

                // 调用算法服务进行训练
                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_JSON);
                
                Map<String, Object> requestMap = new HashMap<>();
                requestMap.put("taskId", trainTask.getId());
                requestMap.put("datasetId", trainTask.getDatasetId());
                requestMap.put("dataset_name", datasetName); 
                requestMap.put("model_name", trainTask.getModelName());
                // requestMap.remove("parameters"); // 如果不需要发送原始 JSON 字符串
                // 同时，检查 Flask 端是否需要其他参数，比如 epochs, batch_size 等，
                // 如果需要，不应该发送 parameters 字符串，而是解析后发送具体字段
                // 例如，Flask 的 start_training 获取了 epochs 和 batch_size
                // 你可能需要这样做：
                requestMap.put("epochs", trainTask.getEpochs());
                requestMap.put("batch_size", trainTask.getBatchSize());
                
                HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestMap, headers);
                
                // 异步调用
                new Thread(() -> {
                    try {
                        // 动态构建完整的 URL
                        String trainEndpoint = algorithmServiceUrl + "/api/train/start";
                        restTemplate.postForEntity(trainEndpoint, requestEntity, String.class);
                        log.info("训练任务 {} 已成功提交到训练服务。", trainTask.getId());
                        // 成功：更新任务状态为“已提交”或“进行中”
                        trainTask.setTaskStatus("RUNNING"); // RUNNING=已提交/进行中
                        trainTask.setErrorMessage(null);
                        trainTaskService.updateById(trainTask);
                    } catch (HttpClientErrorException | HttpServerErrorException httpClientOrServerException) {
                        String errorBody = httpClientOrServerException.getResponseBodyAsString();
                        log.error("提交训练任务 {} 到训练服务失败: {} - Response Body: {}", trainTask.getId(), httpClientOrServerException.getMessage(), errorBody, httpClientOrServerException);
                        trainTask.setTaskStatus("FAILED");
                        // 优先使用详细的错误体，如果获取不到再用 getMessage()
                        trainTask.setErrorMessage(errorBody != null && !errorBody.isEmpty() ? errorBody : httpClientOrServerException.getMessage());
                        trainTaskService.updateById(trainTask);
                    } catch (Exception e) { // 其他类型的异常
                        log.error("提交训练任务 {} 到训练服务时发生非HTTP错误: {}", trainTask.getId(), e.getMessage(), e);
                        trainTask.setTaskStatus("FAILED");
                        trainTask.setErrorMessage(e.getMessage());
                        trainTaskService.updateById(trainTask);
                    }
                }).start();
                
                return Result.success("训练任务创建并已提交训练");
            } catch (Exception e) {
                log.error("训练任务提交准备阶段异常: {}", e.getMessage(), e); // 修改日志信息，更精确
                return Result.success("训练任务创建成功，但提交训练失败");
            }
        } catch (Exception e) {
            log.error("创建训练任务失败: {}", e.getMessage(), e); // 使用 log.error 并打印堆栈
            // e.printStackTrace(); // 打印完整堆栈信息到日志  // 避免在生产代码中使用 printStackTrace
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
        log.info("收到训练任请求: cu务分页查询rrent={}, size={}, name={}, status={}, model_name={}", current, size, name, status, model_name);
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