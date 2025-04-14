package com.example.webspringboot.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rs.entity.TrainTask;
import com.rs.mapper.TrainTaskMapper;
import org.springframework.stereotype.Service;

@Service
public class TrainTaskService extends ServiceImpl<TrainTaskMapper, TrainTask> {
    public Page<TrainTask> pageTrainTasks(Page<TrainTask> page, String name, Integer status) {
        // 构建查询条件
        QueryWrapper<TrainTask> queryWrapper = new QueryWrapper<>();
        if (name != null && !name.trim().isEmpty()) {
            queryWrapper.like("task_name", name);
        }
        if (status != null) {
            queryWrapper.eq("task_status", status);
        }
        
        // 执行分页查询
        return this.page(page, queryWrapper);
    }
}