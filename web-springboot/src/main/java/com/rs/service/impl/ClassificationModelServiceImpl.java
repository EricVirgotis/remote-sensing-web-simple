package com.rs.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rs.entity.ClassificationModel;
import com.rs.entity.TrainingTask; // 新增导入
import com.rs.exception.BusinessException;
import com.rs.mapper.ClassificationModelMapper;
import com.rs.mapper.TrainingTaskMapper; // 新增导入
import com.rs.service.ClassificationModelService;
import com.rs.utils.UserContext; // 新增导入
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired; // 新增导入
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List; // 新增导入
import java.util.stream.Collectors; // 新增导入
import java.util.stream.Stream; // 新增导入

/**
 * 分类模型服务实现类
 */
@Slf4j
@Service
public class ClassificationModelServiceImpl extends ServiceImpl<ClassificationModelMapper, ClassificationModel> implements ClassificationModelService {

    @Autowired // 新增注入
    private TrainingTaskMapper trainingTaskMapper;

    @Override
    public ClassificationModel getModelDetail(Long modelId) {
        ClassificationModel model = this.getById(modelId);
        if (model == null) {
            throw new BusinessException("模型不存在");
        }
        return model;
    }

    /**
     * 构建基础的模型查询条件
     */
    private LambdaQueryWrapper<ClassificationModel> buildBaseModelQueryWrapper() {
        LambdaQueryWrapper<ClassificationModel> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(ClassificationModel::getStatus, 1)
                   .eq(ClassificationModel::getDeleted, 0);
        return queryWrapper;
    }

    /**
     * 检查模型名称是否已存在
     */
    private void checkModelNameExists(String modelName, Long excludeModelId) {
        LambdaQueryWrapper<ClassificationModel> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(ClassificationModel::getModelName, modelName);
        if (excludeModelId != null) {
            queryWrapper.ne(ClassificationModel::getId, excludeModelId);
        }
        if (this.count(queryWrapper) > 0) {
            throw new BusinessException("模型名称已存在");
        }
    }

    @Override
    public Page<ClassificationModel> getModelPage(Page<ClassificationModel> page, String modelName, String modelType) {
        Long userId = UserContext.getUserId();
        if (userId == null) {
            log.warn("用户未登录，无法获取模型分页列表");
            return new Page<>(page.getCurrent(), page.getSize(), 0);
        }

        LambdaQueryWrapper<ClassificationModel> queryWrapper = buildBaseModelQueryWrapper();
        queryWrapper.like(modelName != null, ClassificationModel::getModelName, modelName)
                   .eq(modelType != null, ClassificationModel::getModelType, modelType)
                   .eq(ClassificationModel::getUserId, userId)
                   .eq(ClassificationModel::getIsDefault, 0)
                   .orderByDesc(ClassificationModel::getCreateTime);

        return this.page(page, queryWrapper);
    }

    @Override
    public List<ClassificationModel> getAvailableModelsForUser() {
        Long userId = UserContext.getUserId();
        if (userId == null) {
            throw new BusinessException("用户未登录，无法获取模型列表");
        }

        // 1. 获取所有启用的默认模型
        LambdaQueryWrapper<ClassificationModel> defaultModelWrapper = buildBaseModelQueryWrapper();
        defaultModelWrapper.eq(ClassificationModel::getIsDefault, 1);
        List<ClassificationModel> defaultModels = this.list(defaultModelWrapper);

        // 2. 获取当前用户创建的、启用的非默认模型
        LambdaQueryWrapper<ClassificationModel> userModelWrapper = buildBaseModelQueryWrapper();
        userModelWrapper.eq(ClassificationModel::getUserId, userId)
                       .eq(ClassificationModel::getIsDefault, 0);
        List<ClassificationModel> userModels = this.list(userModelWrapper);

        // 3. 合并列表
        // 使用 Stream API 合并并去重（虽然理论上不应有重复，但以防万一）
        List<ClassificationModel> availableModels = Stream.concat(defaultModels.stream(), userModels.stream())
                                                          .distinct() // 基于 ClassificationModel 的 equals/hashCode 去重
                                                          .collect(Collectors.toList());

        // 4. 按模型名称和精度排序，方便前端展示
        availableModels.sort((m1, m2) -> {
            int nameCompare = m1.getModelName().compareToIgnoreCase(m2.getModelName());
            if (nameCompare != 0) {
                return nameCompare;
            }
            // 名称相同，则按精度降序排（精度高的在前）
            // 处理 null 值，假设 null 精度最低
            if (m1.getAccuracy() == null && m2.getAccuracy() == null) return 0;
            if (m1.getAccuracy() == null) return 1; // m1 null, m2 not null -> m2 > m1
            if (m2.getAccuracy() == null) return -1; // m1 not null, m2 null -> m1 > m2
            return m2.getAccuracy().compareTo(m1.getAccuracy()); // 降序
        });

        return availableModels;
    }


    @Override
    @Transactional(rollbackFor = Exception.class)
    public Long addModel(ClassificationModel model) {
        checkModelNameExists(model.getModelName(), null);

        model.setStatus(1);
        model.setIsDefault(0);
        model.setCreateTime(LocalDateTime.now());
        model.setUpdateTime(LocalDateTime.now());

        this.save(model);
        return model.getId();
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateModel(ClassificationModel model) {
        ClassificationModel existModel = this.getById(model.getId());
        if (existModel == null) {
            throw new BusinessException("模型不存在");
        }

        if (!existModel.getModelName().equals(model.getModelName())) {
            checkModelNameExists(model.getModelName(), model.getId());
        }

        model.setUpdateTime(LocalDateTime.now());
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