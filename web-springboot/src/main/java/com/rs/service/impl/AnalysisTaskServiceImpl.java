package com.rs.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rs.common.Constants;
import com.rs.dto.AnalysisTaskSubmitDTO;
import com.rs.entity.AnalysisTask;
import com.rs.entity.ClassificationModel;
import com.rs.entity.RemoteImage;
import com.rs.exception.BusinessException;
import com.rs.mapper.AnalysisTaskMapper;
import com.rs.service.AnalysisTaskService;
import com.rs.service.ClassificationModelService;
import com.rs.service.RemoteImageService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * 分析任务服务实现类
 */
@Slf4j
@Service
public class AnalysisTaskServiceImpl extends ServiceImpl<AnalysisTaskMapper, AnalysisTask> implements AnalysisTaskService {

    @Autowired
    private RemoteImageService remoteImageService;
    
    @Autowired
    private ClassificationModelService classificationModelService;
    
    @Autowired
    private RestTemplate restTemplate;
    
    @Value("${rs.algorithm.url}")
    private String algorithmServiceUrl;
    
    @Value("${rs.file-storage.result-path}")
    private String resultPath;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Long submitTask(Long userId, AnalysisTaskSubmitDTO submitDTO) {
        // 检查影像是否存在
        RemoteImage remoteImage = remoteImageService.getById(submitDTO.getImageId());
        if (remoteImage == null) {
            throw new BusinessException("影像不存在");
        }
        
        // 检查影像所有权
        if (!remoteImage.getUserId().equals(userId)) {
            throw new BusinessException("无权操作此影像");
        }
        
        // 检查模型是否存在
        ClassificationModel model = classificationModelService.getById(submitDTO.getModelId());
        if (model == null) {
            throw new BusinessException("模型不存在");
        }
        
        // 检查模型状态
        if (model.getStatus() != 1) {
            throw new BusinessException("模型已禁用");
        }
        
        // 创建任务
        AnalysisTask task = new AnalysisTask();
        task.setUserId(userId);
        task.setImageId(submitDTO.getImageId());
        task.setModelId(submitDTO.getModelId());
        task.setTaskName(submitDTO.getTaskName() != null ? submitDTO.getTaskName() : 
                         remoteImage.getImageName() + "_" + model.getModelName());
        task.setTaskStatus(Constants.TaskStatus.PENDING);
        task.setParameters(submitDTO.getParameters());
        task.setCreateTime(LocalDateTime.now());
        task.setUpdateTime(LocalDateTime.now());
        
        // 保存任务
        this.save(task);
        
        // 异步提交到算法服务
        submitToAlgorithmService(task, remoteImage, model);
        
        return task.getId();
    }

    @Override
    public AnalysisTask getTaskDetail(Long taskId) {
        AnalysisTask task = this.getById(taskId);
        if (task == null) {
            throw new BusinessException("任务不存在");
        }
        return task;
    }

    @Override
    public Page<AnalysisTask> getUserTaskPage(Page<AnalysisTask> page, Long userId, String taskName, String taskStatus) {
        LambdaQueryWrapper<AnalysisTask> queryWrapper = new LambdaQueryWrapper<>();
        // 添加查询条件
        queryWrapper.eq(AnalysisTask::getUserId, userId);
        queryWrapper.like(taskName != null, AnalysisTask::getTaskName, taskName);
        queryWrapper.eq(taskStatus != null, AnalysisTask::getTaskStatus, taskStatus);
        // 按创建时间降序排序
        queryWrapper.orderByDesc(AnalysisTask::getCreateTime);
        
        return this.page(page, queryWrapper);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean cancelTask(Long userId, Long taskId) {
        // 查询任务
        AnalysisTask task = this.getById(taskId);
        if (task == null) {
            throw new BusinessException("任务不存在");
        }
        
        // 检查权限
        if (!task.getUserId().equals(userId)) {
            throw new BusinessException("无权操作此任务");
        }
        
        // 检查任务状态
        if (Constants.TaskStatus.COMPLETED.equals(task.getTaskStatus()) || 
            Constants.TaskStatus.FAILED.equals(task.getTaskStatus())) {
            throw new BusinessException("任务已完成或失败，无法取消");
        }
        
        // 更新任务状态
        task.setTaskStatus(Constants.TaskStatus.CANCELED);
        task.setEndTime(LocalDateTime.now());
        task.setUpdateTime(LocalDateTime.now());
        
        // 通知算法服务取消任务（如果需要）
        try {
            String cancelUrl = algorithmServiceUrl + "/task/cancel/" + taskId;
            restTemplate.postForEntity(cancelUrl, null, String.class);
        } catch (Exception e) {
            log.error("通知算法服务取消任务失败", e);
            // 继续执行，至少完成数据库的状态更新
        }
        
        return this.updateById(task);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean deleteTask(Long userId, Long taskId) {
        // 查询任务
        AnalysisTask task = this.getById(taskId);
        if (task == null) {
            throw new BusinessException("任务不存在");
        }
        
        // 检查权限
        if (!task.getUserId().equals(userId)) {
            throw new BusinessException("无权操作此任务");
        }
        
        // 检查任务状态
        if (Constants.TaskStatus.RUNNING.equals(task.getTaskStatus())) {
            throw new BusinessException("任务正在运行中，无法删除");
        }
        
        // 逻辑删除任务
        return this.removeById(taskId);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateTaskStatus(Long taskId, String taskStatus, String resultPath, String errorMessage) {
        // 查询任务
        AnalysisTask task = this.getById(taskId);
        if (task == null) {
            throw new BusinessException("任务不存在");
        }
        
        // 更新任务状态
        task.setTaskStatus(taskStatus);
        
        // 根据状态设置相关字段
        if (Constants.TaskStatus.RUNNING.equals(taskStatus)) {
            task.setStartTime(LocalDateTime.now());
        } else if (Constants.TaskStatus.COMPLETED.equals(taskStatus) || 
                   Constants.TaskStatus.FAILED.equals(taskStatus)) {
            task.setEndTime(LocalDateTime.now());
            task.setResultPath(resultPath);
            task.setErrorMessage(errorMessage);
        }
        
        task.setUpdateTime(LocalDateTime.now());
        
        return this.updateById(task);
    }
    
    /**
     * 提交任务到算法服务
     *
     * @param task 任务
     * @param remoteImage 遥感影像
     * @param model 分类模型
     */
    private void submitToAlgorithmService(AnalysisTask task, RemoteImage remoteImage, ClassificationModel model) {
        try {
            // 构建请求参数
            Map<String, Object> requestMap = new HashMap<>();
            requestMap.put("taskId", task.getId());
            requestMap.put("imagePath", remoteImage.getImagePath());
            requestMap.put("modelPath", model.getModelPath());
            requestMap.put("resultPath", resultPath + "/" + task.getId());
            requestMap.put("parameters", task.getParameters());
            
            // 设置请求头
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            // 发送请求
            HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestMap, headers);
            String submitUrl = algorithmServiceUrl + "/task/submit";
            
            // 异步提交任务
            new Thread(() -> {
                try {
                    // 更新任务状态为运行中
                    updateTaskStatus(task.getId(), Constants.TaskStatus.RUNNING, null, null);
                    
                    // 发送请求到算法服务
                    ResponseEntity<String> response = restTemplate.postForEntity(submitUrl, requestEntity, String.class);
                    
                    log.info("提交任务到算法服务成功，任务ID：{}，响应：{}", task.getId(), response.getBody());
                } catch (Exception e) {
                    log.error("提交任务到算法服务失败", e);
                    // 更新任务状态为失败
                    updateTaskStatus(task.getId(), Constants.TaskStatus.FAILED, null, "提交任务到算法服务失败：" + e.getMessage());
                }
            }).start();
            
        } catch (Exception e) {
            log.error("准备提交任务到算法服务失败", e);
            // 更新任务状态为失败
            updateTaskStatus(task.getId(), Constants.TaskStatus.FAILED, null, "准备提交任务到算法服务失败：" + e.getMessage());
        }
    }
}