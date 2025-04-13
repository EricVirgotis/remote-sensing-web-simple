package com.example.webspringboot.controller;

import com.example.webspringboot.service.TrainTaskService;
import com.rs.common.Result;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.rs.entity.TrainTask;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/train-task")
public class TrainTaskController {
    private final TrainTaskService trainTaskService;

    public TrainTaskController(TrainTaskService trainTaskService) {
        this.trainTaskService = trainTaskService;
    }

    @GetMapping("/page")
    public Result<Page<TrainTask>> pageTrainTasks(
        @RequestParam Integer current,
        @RequestParam Integer size,
        @RequestParam(required = false) String name,
        @RequestParam(required = false) Integer status
    ) {
        try {
            Page<TrainTask> page = new Page<>(current, size);
            Page<TrainTask> result = trainTaskService.pageTrainTasks(page, name, status);
            return Result.success(result != null ? result : page);
        } catch (Exception e) {
            return Result.error(500, "查询训练任务列表失败: " + e.getMessage());
        }
    }
}