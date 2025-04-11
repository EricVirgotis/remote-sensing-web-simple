package com.rs.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rs.entity.ClassificationModel;
import com.rs.exception.BusinessException;
import com.rs.mapper.ClassificationModelMapper;
import com.rs.service.ClassificationModelService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

/**
 * 分类模型服务实现类
 */
@Slf4j
@Service
public class ClassificationModelServiceImpl extends ServiceImpl<ClassificationModelMapper, ClassificationModel> implements ClassificationModelService {

    @Override
    public ClassificationModel getModelDetail(Long modelId) {
        ClassificationModel model = this.getById(modelId);
        if (model == null) {
            throw new BusinessException("模型不存在");
        }
        return model;
    }

    @Override
    public Page<ClassificationModel> getModelPage(Page<ClassificationModel> page, String modelName, String modelType) {
        LambdaQueryWrapper<ClassificationModel> queryWrapper = new LambdaQueryWrapper<>();
        // 添加查询条件
        queryWrapper.like(modelName != null, ClassificationModel::getModelName, modelName);
        queryWrapper.eq(modelType != null, ClassificationModel::getModelType, modelType);
        // 只查询启用的模型
        queryWrapper.eq(ClassificationModel::getStatus, 1);
        // 按创建时间降序排序
        queryWrapper.orderByDesc(ClassificationModel::getCreateTime);
        
        return this.page(page, queryWrapper);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Long addModel(ClassificationModel model) {
        // 检查模型名称是否已存在
        LambdaQueryWrapper<ClassificationModel> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(ClassificationModel::getModelName, model.getModelName());
        if (this.count(queryWrapper) > 0) {
            throw new BusinessException("模型名称已存在");
        }
        
        // 设置默认值
        model.setStatus(1); // 默认启用
        model.setIsDefault(0); // 默认非默认模型
        model.setCreateTime(LocalDateTime.now());
        model.setUpdateTime(LocalDateTime.now());
        
        // 保存模型
        this.save(model);
        
        return model.getId();
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateModel(ClassificationModel model) {
        // 检查模型是否存在
        ClassificationModel existModel = this.getById(model.getId());
        if (existModel == null) {
            throw new BusinessException("模型不存在");
        }
        
        // 检查模型名称是否已存在（排除自身）
        if (!existModel.getModelName().equals(model.getModelName())) {
            LambdaQueryWrapper<ClassificationModel> queryWrapper = new LambdaQueryWrapper<>();
            queryWrapper.eq(ClassificationModel::getModelName, model.getModelName());
            queryWrapper.ne(ClassificationModel::getId, model.getId());
            if (this.count(queryWrapper) > 0) {
                throw new BusinessException("模型名称已存在");
            }
        }
        
        // 更新时间
        model.setUpdateTime(LocalDateTime.now());
        
        // 保留原有字段
        model.setCreateTime(existModel.getCreateTime());
        model.setIsDefault(existModel.getIsDefault());
        
        return this.updateById(model);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateModelStatus(Long modelId, Integer status) {
        // 检查模型是否存在
        ClassificationModel model = this.getById(modelId);
        if (model == null) {
            throw new BusinessException("模型不存在");
        }
        
        // 如果是默认模型且要禁用，则不允许操作
        if (model.getIsDefault() == 1 && status == 0) {
            throw new BusinessException("默认模型不能禁用");
        }
        
        // 更新状态
        model.setStatus(status);
        model.setUpdateTime(LocalDateTime.now());
        
        return this.updateById(model);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean setDefaultModel(Long modelId) {
        // 检查模型是否存在
        ClassificationModel model = this.getById(modelId);
        if (model == null) {
            throw new BusinessException("模型不存在");
        }
        
        // 检查模型状态
        if (model.getStatus() != 1) {
            throw new BusinessException("禁用的模型不能设为默认模型");
        }
        
        // 先将所有模型设为非默认
        LambdaQueryWrapper<ClassificationModel> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(ClassificationModel::getIsDefault, 1);
        ClassificationModel defaultModel = this.getOne(queryWrapper);
        
        if (defaultModel != null) {
            defaultModel.setIsDefault(0);
            defaultModel.setUpdateTime(LocalDateTime.now());
            this.updateById(defaultModel);
        }
        
        // 设置新的默认模型
        model.setIsDefault(1);
        model.setUpdateTime(LocalDateTime.now());
        
        return this.updateById(model);
    }

    @Override
    public ClassificationModel getDefaultModel() {
        LambdaQueryWrapper<ClassificationModel> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(ClassificationModel::getIsDefault, 1);
        queryWrapper.eq(ClassificationModel::getStatus, 1);
        
        ClassificationModel defaultModel = this.getOne(queryWrapper);
        if (defaultModel == null) {
            // 如果没有默认模型，则返回第一个启用的模型
            LambdaQueryWrapper<ClassificationModel> fallbackQueryWrapper = new LambdaQueryWrapper<>();
            fallbackQueryWrapper.eq(ClassificationModel::getStatus, 1);
            fallbackQueryWrapper.orderByDesc(ClassificationModel::getCreateTime);
            fallbackQueryWrapper.last("LIMIT 1");
            
            defaultModel = this.getOne(fallbackQueryWrapper);
            
            // 如果仍然没有，则抛出异常
            if (defaultModel == null) {
                throw new BusinessException("系统中没有可用的分类模型");
            }
        }
        
        return defaultModel;
    }
}