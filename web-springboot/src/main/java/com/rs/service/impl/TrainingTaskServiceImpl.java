package com.rs.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rs.entity.ClassificationModel;
import com.rs.entity.TrainingTask;
import com.rs.mapper.ClassificationModelMapper;
import com.rs.mapper.TrainingTaskMapper;
import com.rs.service.TrainingTaskService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;

/**
 * 训练任务服务实现类
 */
@Slf4j
@Service
public class TrainingTaskServiceImpl extends ServiceImpl<TrainingTaskMapper, TrainingTask> implements TrainingTaskService {

    @Autowired
    private ClassificationModelMapper classificationModelMapper;
    
    @Autowired
    private JdbcTemplate jdbcTemplate;

    /**
     * 更新训练任务状态
     * @param taskId 任务ID
     * @param taskStatus 任务状态
     * @param modelPath 模型路径
     * @param accuracy 模型精度
     * @param errorMessage 错误信息
     * @return 是否更新成功
     */
    @Transactional
    public boolean updateTaskStatus(Long taskId, String taskStatus, String modelPath, BigDecimal accuracy, String errorMessage) {
        // 1. 获取训练任务
        TrainingTask task = this.getById(taskId);
        if (task == null) {
            log.error("训练任务不存在: {}", taskId);
            return false;
        }
        
        // 2. 更新训练任务状态
        task.setTaskStatus(taskStatus);
        if (modelPath != null) {
            task.setModelPath(modelPath);
        }
        if (accuracy != null) {
            task.setAccuracy(accuracy);
        }
        if (errorMessage != null) {
            task.setErrorMessage(errorMessage);
        }
        
        boolean updated = this.updateById(task);
        
        // 3. 如果任务状态为已完成，则自动将模型数据插入到分类模型表
        if (updated && "COMPLETED".equals(taskStatus)) {
            insertModelFromTrainingTask(task);
        }
        
        return updated;
    }
    
    /**
     * 将训练任务生成的模型数据插入到分类模型表
     * @param task 训练任务
     */
    private void insertModelFromTrainingTask(TrainingTask task) {
        try {
            // 方法一：使用JdbcTemplate执行SQL语句
            String sql = "INSERT INTO classification_model (user_id, model_name, model_path, model_type, description, accuracy, parameters, is_default, status) " +
                    "VALUES (?, ?, ?, ?, ?, ?, ?, 0, 1)";
            
            jdbcTemplate.update(sql,
                    task.getUserId(), // 新增 userId
                    task.getModelName(),
                    task.getModelPath(),
                    task.getModelType(),
                    "由训练任务 \"" + task.getTaskName() + "\" 生成的模型",
                    task.getAccuracy(),
                    task.getParameters());
            
            log.info("成功将训练任务 {} 生成的模型插入到分类模型表", task.getId());
            
            // 方法二：使用MyBatis-Plus插入
            /*
            ClassificationModel model = new ClassificationModel();
            model.setUserId(task.getUserId()); // 新增 userId
            model.setModelName(task.getModelName());
            model.setModelPath(task.getModelPath());
            model.setModelType(task.getModelType());
            model.setDescription("由训练任务 \"" + task.getTaskName() + "\" 生成的模型");
            model.setAccuracy(task.getAccuracy());
            model.setParameters(task.getParameters());
            model.setIsDefault(0); // 非默认模型
            model.setStatus(1); // 启用状态
            
            classificationModelMapper.insert(model);
            */
        } catch (Exception e) {
            log.error("将训练任务生成的模型插入到分类模型表失败: {}", e.getMessage(), e);
        }
    }
}