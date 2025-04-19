package com.rs.controller;

import com.rs.common.Result;
import com.rs.entity.TrainingTask;
import com.rs.service.TrainingTaskService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;

/**
 * 训练任务控制器
 */
@Slf4j
@RestController
@RequestMapping("/api/training-tasks")
public class TrainingTaskController {

    @Autowired
    private TrainingTaskService trainingTaskService;

    /**
     * 更新训练任务状态
     * @param taskId 任务ID
     * @param taskStatus 任务状态
     * @param modelPath 模型路径
     * @param accuracy 模型精度
     * @param errorMessage 错误信息
     * @return 更新结果
     */
    @PutMapping("/{taskId}/status")
    public Result<Boolean> updateTaskStatus(
            @PathVariable Long taskId,
            @RequestParam String taskStatus,
            @RequestParam(required = false) String modelPath,
            @RequestParam(required = false) BigDecimal accuracy,
            @RequestParam(required = false) String errorMessage) {
        
        log.info("更新训练任务状态: taskId={}, status={}", taskId, taskStatus);
        boolean updated = trainingTaskService.updateTaskStatus(taskId, taskStatus, modelPath, accuracy, errorMessage);
        
        if (updated) {
            return Result.success("更新训练任务状态成功", true);
        } else {
            return Result.error("更新训练任务状态失败");
        }
    }

    /**
     * 获取训练任务详情
     * @param taskId 任务ID
     * @return 训练任务详情
     */
    @GetMapping("/{taskId}")
    public Result<TrainingTask> getTaskDetail(@PathVariable Long taskId) {
        TrainingTask task = trainingTaskService.getById(taskId);
        if (task != null) {
            return Result.success(task);
        } else {
            return Result.error("训练任务不存在");
        }
    }
}