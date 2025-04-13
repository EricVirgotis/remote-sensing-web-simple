package com.example.webspringboot.controller;

import com.example.webspringboot.service.TrainTaskService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/train-task")
public class TrainTaskController {
    private final TrainTaskService trainTaskService;

    public TrainTaskController(TrainTaskService trainTaskService) {
        this.trainTaskService = trainTaskService;
    }

    @GetMapping("/page")
    public Object pageTrainTasks(Integer current, Integer size, String name, Integer status) {
        return trainTaskService.pageTrainTasks(current, size, name, status);
    }
}