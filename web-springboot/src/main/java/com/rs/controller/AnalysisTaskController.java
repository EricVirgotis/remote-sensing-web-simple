package com.rs.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.rs.common.Result;
import com.rs.dto.AnalysisTaskSubmitDTO;
import com.rs.entity.AnalysisTask;
import com.rs.service.AnalysisTaskService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 分析任务控制器
 */
@Tag(name = "分析任务管理", description = "分析任务相关接口")
@RestController
@RequestMapping("/api/tasks")
public class AnalysisTaskController {

    @Autowired
    private AnalysisTaskService analysisTaskService;

    @Operation(summary = "提交分析任务")
    @PostMapping
    public Result<Long> submitTask(
            @Parameter(description = "用户ID") @RequestHeader("X-User-ID") Long userId,
            @RequestBody AnalysisTaskSubmitDTO submitDTO) {
        return Result.success(analysisTaskService.submitTask(userId, submitDTO));
    }

    @Operation(summary = "获取任务详情")
    @GetMapping("/{taskId}")
    public Result<AnalysisTask> getTaskDetail(
            @Parameter(description = "任务ID") @PathVariable Long taskId) {
        return Result.success(analysisTaskService.getTaskDetail(taskId));
    }

    @Operation(summary = "分页查询用户的任务列表")
    @GetMapping("/page")
    public Result<Page<AnalysisTask>> getUserTaskPage(
            @Parameter(description = "用户ID") @RequestHeader("X-User-ID") Long userId,
            @Parameter(description = "页码") @RequestParam(defaultValue = "1") Integer current,
            @Parameter(description = "每页条数") @RequestParam(defaultValue = "10") Integer size,
            @Parameter(description = "任务名称") @RequestParam(required = false) String taskName,
            @Parameter(description = "任务状态") @RequestParam(required = false) String taskStatus) {
        Page<AnalysisTask> page = new Page<>(current, size);
        return Result.success(analysisTaskService.getUserTaskPage(page, userId, taskName, taskStatus));
    }

    @Operation(summary = "取消任务")
    @PutMapping("/{taskId}/cancel")
    public Result<Boolean> cancelTask(
            @Parameter(description = "用户ID") @RequestHeader("X-User-ID") Long userId,
            @Parameter(description = "任务ID") @PathVariable Long taskId) {
        return Result.success(analysisTaskService.cancelTask(userId, taskId));
    }

    @Operation(summary = "删除任务")
    @DeleteMapping("/{taskId}")
    public Result<Boolean> deleteTask(
            @Parameter(description = "用户ID") @RequestHeader("X-User-ID") Long userId,
            @Parameter(description = "任务ID") @PathVariable Long taskId) {
        return Result.success(analysisTaskService.deleteTask(userId, taskId));
    }

    @Operation(summary = "更新任务状态（算法服务回调）")
    @PutMapping("/{taskId}/status")
    public Result<Boolean> updateTaskStatus(
            @Parameter(description = "任务ID") @PathVariable Long taskId,
            @Parameter(description = "任务状态") @RequestParam String taskStatus,
            @Parameter(description = "结果路径") @RequestParam(required = false) String resultPath,
            @Parameter(description = "错误信息") @RequestParam(required = false) String errorMessage) {
        return Result.success(analysisTaskService.updateTaskStatus(taskId, taskStatus, resultPath, errorMessage));
    }
}