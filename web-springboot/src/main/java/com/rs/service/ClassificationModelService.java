package com.rs.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.rs.entity.ClassificationModel;

/**
 * 分类模型服务接口
 */
public interface ClassificationModelService extends IService<ClassificationModel> {
    
    /**
     * 获取模型详情
     *
     * @param modelId 模型ID
     * @return 模型信息
     */
    ClassificationModel getModelDetail(Long modelId);
    
    /**
     * 分页查询模型列表
     *
     * @param page 分页参数
     * @param modelName 模型名称
     * @param modelType 模型类型
     * @return 模型列表
     */
    Page<ClassificationModel> getModelPage(Page<ClassificationModel> page, String modelName, String modelType);
    
    /**
     * 添加模型
     *
     * @param model 模型信息
     * @return 模型ID
     */
    Long addModel(ClassificationModel model);
    
    /**
     * 更新模型信息
     *
     * @param model 模型信息
     * @return 是否成功
     */
    boolean updateModel(ClassificationModel model);
    
    /**
     * 修改模型状态
     *
     * @param modelId 模型ID
     * @param status 状态
     * @return 是否成功
     */
    boolean updateModelStatus(Long modelId, Integer status);
    
    /**
     * 设置默认模型
     *
     * @param modelId 模型ID
     * @return 是否成功
     */
    boolean setDefaultModel(Long modelId);
    
    /**
     * 获取默认模型
     *
     * @return 默认模型
     */
    ClassificationModel getDefaultModel();
}