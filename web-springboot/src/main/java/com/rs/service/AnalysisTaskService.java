package com.rs.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.rs.dto.AnalysisTaskSubmitDTO;
import com.rs.entity.AnalysisTask;

/**
 * 分析任务服务接口
 */
public interface AnalysisTaskService extends IService<AnalysisTask> {
    
    /**
     * 提交分析任务
     *
     * @param userId 用户ID
     * @param submitDTO 任务提交信息
     * @return 任务ID
     */
    Long submitTask(Long userId, AnalysisTaskSubmitDTO submitDTO);
    
    /**
     * 获取任务详情
     *
     * @param taskId 任务ID
     * @return 任务信息
     */
    AnalysisTask getTaskDetail(Long taskId);
    
    /**
     * 分页查询用户的任务列表
     *
     * @param page 分页参数
     * @param userId 用户ID
     * @param taskName 任务名称
     * @param taskStatus 任务状态
     * @return 任务列表
     */
    Page<AnalysisTask> getUserTaskPage(Page<AnalysisTask> page, Long userId, String taskName, String taskStatus);
    
    /**
     * 取消任务
     *
     * @param userId 用户ID
     * @param taskId 任务ID
     * @return 是否成功
     */
    boolean cancelTask(Long userId, Long taskId);
    
    /**
     * 删除任务
     *
     * @param userId 用户ID
     * @param taskId 任务ID
     * @return 是否成功
     */
    boolean deleteTask(Long userId, Long taskId);
    
    /**
     * 更新任务状态
     *
     * @param taskId 任务ID
     * @param taskStatus 任务状态
     * @param resultPath 结果路径
     * @param errorMessage 错误信息
     * @return 是否成功
     */
    boolean updateTaskStatus(Long taskId, String taskStatus, String resultPath, String errorMessage);
}