package com.rs.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.rs.common.Result;
import com.rs.entity.ClassificationModel;
import com.rs.service.ClassificationModelService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 分类模型控制器
 */
@Tag(name = "分类模型管理", description = "分类模型相关接口")
@RestController
@RequestMapping("/models")
public class ClassificationModelController {

    @Autowired
    private ClassificationModelService classificationModelService;

    @Operation(summary = "获取模型详情")
    @GetMapping("/{modelId}")
    public Result<ClassificationModel> getModelDetail(
            @Parameter(description = "模型ID") @PathVariable Long modelId) {
        return Result.success(classificationModelService.getModelDetail(modelId));
    }

    @Operation(summary = "分页查询模型列表")
    @GetMapping("/page")
    public Result<Page<ClassificationModel>> getModelPage(
            @Parameter(description = "页码") @RequestParam(defaultValue = "1") Integer current,
            @Parameter(description = "每页条数") @RequestParam(defaultValue = "10") Integer size,
            @Parameter(description = "模型名称") @RequestParam(required = false) String modelName,
            @Parameter(description = "模型类型") @RequestParam(required = false) String modelType) {
        Page<ClassificationModel> page = new Page<>(current, size);
        return Result.success(classificationModelService.getModelPage(page, modelName, modelType));
    }

    @Operation(summary = "添加模型")
    @PostMapping
    public Result<Long> addModel(@RequestBody ClassificationModel model) {
        return Result.success(classificationModelService.addModel(model));
    }

    @Operation(summary = "更新模型信息")
    @PutMapping
    public Result<Boolean> updateModel(@RequestBody ClassificationModel model) {
        return Result.success(classificationModelService.updateModel(model));
    }

    @Operation(summary = "修改模型状态")
    @PutMapping("/{modelId}/status/{status}")
    public Result<Boolean> updateModelStatus(
            @Parameter(description = "模型ID") @PathVariable Long modelId,
            @Parameter(description = "状态：0-禁用，1-启用") @PathVariable Integer status) {
        return Result.success(classificationModelService.updateModelStatus(modelId, status));
    }

    @Operation(summary = "设置默认模型")
    @PutMapping("/{modelId}/default")
    public Result<Boolean> setDefaultModel(
            @Parameter(description = "模型ID") @PathVariable Long modelId) {
        return Result.success(classificationModelService.setDefaultModel(modelId));
    }

    @Operation(summary = "获取默认模型")
    @GetMapping("/default")
    public Result<ClassificationModel> getDefaultModel() {
        return Result.success(classificationModelService.getDefaultModel());
    }
}