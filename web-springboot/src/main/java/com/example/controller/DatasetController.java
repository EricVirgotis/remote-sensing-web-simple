package com.example.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.http.MediaType;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.rs.common.Result;
import com.example.entity.Dataset;
import com.example.service.DatasetService;
import org.springframework.beans.factory.annotation.Autowired;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import jakarta.servlet.http.HttpServletResponse;

@RestController
@RequestMapping("/dataset")
public class DatasetController {
    
    private Long checkAndGetUserId() {
        Long userId = tokenUtils.getCurrentUserId();
        if (userId == null) {
            throw new com.rs.exception.BusinessException(401, "用户未认证");
        }
        return userId;
    }

    @PostMapping("/upload")
    public Result<Long> createDataset(
        @RequestParam("file") MultipartFile file,
        @RequestParam(required = false) String name,
        @RequestParam(required = false) String description
    ) {
        try {
            Long userId = checkAndGetUserId();
            Long datasetId = datasetService.uploadDataset(userId, file, name, description);
            return Result.success(datasetId);
        } catch (com.rs.exception.BusinessException e) {
            return Result.error(e.getCode(), e.getMessage());
        } catch (Exception e) {
            return Result.error(500, "上传数据集失败: " + e.getMessage());
        }
    }
    
    @Autowired
    private DatasetService datasetService;
    
    @Autowired
    private com.rs.utils.TokenUtils tokenUtils;
    
    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public Result<Dataset> createDataset(
            @RequestPart("dataset") Dataset dataset,
            @RequestPart(value = "file", required = false) MultipartFile file
    ) {
        try {
            Long userId = checkAndGetUserId();
            dataset.setUserId(userId);
            Dataset createdDataset = datasetService.createDataset(dataset, file);
            return Result.success(createdDataset);
        } catch (com.rs.exception.BusinessException e) {
            return Result.error(e.getCode(), e.getMessage());
        } catch (Exception e) {
            return Result.error(500, "创建数据集失败: " + e.getMessage());
        }
    }
    
    @GetMapping("/list_datasets")
    public Result<Page<Dataset>> pageDatasets(
        @RequestParam Integer current,
        @RequestParam Integer size,
        @RequestParam(required = false) String name,
        @RequestParam(required = false) Integer status
    ) {
        try {
            Page<Dataset> page = new Page<>(current, size);
            // 调用Service层进行分页查询
            Page<Dataset> result = datasetService.pageDatasets(page, name, status);
            return Result.success(result);
        } catch (Exception e) {
            return Result.error(500, "查询数据集列表失败: " + e.getMessage());
        }
    }
    
    @GetMapping("/{id}")
    public Result<Dataset> getDatasetDetail(@PathVariable Long id) {
        try {
            // 调用Service层查询数据集详情
            Dataset dataset = datasetService.getDatasetDetail(id);
            return Result.success(dataset);
        } catch (Exception e) {
            return Result.error(500, "获取数据集详情失败: " + e.getMessage());
        }
    }
    
    @DeleteMapping("/{id}")
    public Result<Boolean> deleteDataset(@PathVariable Long id) {
        try {
            // 调用Service层删除数据集
            boolean result = datasetService.deleteDataset(id);
            return Result.success(result);
        } catch (Exception e) {
            return Result.error(500, "删除数据集失败: " + e.getMessage());
        }
    }
    
    private String getDatasetFilePath(Long id) {
        // 调用Service层获取数据集文件路径
        return datasetService.getDatasetPath(id);
    }
    
    @GetMapping("/{id}/download")
    public void downloadDataset(@PathVariable Long id, HttpServletResponse response) throws IOException {
        try {
            // 获取数据集文件路径
            String filePath = getDatasetFilePath(id);
            File file = new File(filePath);
            
            if (!file.exists()) {
                response.sendError(HttpServletResponse.SC_NOT_FOUND, "数据集文件不存在");
                return;
            }
            
            // 设置响应头
            response.setContentType("application/octet-stream");
            response.setHeader("Content-Disposition", "attachment; filename=" + file.getName());
            response.setContentLength((int) file.length());
            
            // 文件流拷贝
            try (InputStream in = new FileInputStream(file);
                 OutputStream out = response.getOutputStream()) {
                byte[] buffer = new byte[4096];
                int bytesRead;
                while ((bytesRead = in.read(buffer)) != -1) {
                    out.write(buffer, 0, bytesRead);
                }
            }
        } catch (Exception e) {
            response.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "下载数据集失败: " + e.getMessage());
        }
    }
    
    @PutMapping("/{id}")
    public Result<Boolean> updateDataset(
        @PathVariable Long id,
        @RequestParam(value = "file", required = false) MultipartFile file,
        @RequestParam String name,
        @RequestParam String description,
        @RequestParam Integer status
    ) {
        try {
            // 验证必要参数
            if (name == null || name.trim().isEmpty()) {
                return Result.error(400, "数据集名称不能为空");
            }
            if (status == null || status < 0 || status > 2) {
                return Result.error(400, "状态值不合法");
            }
            
            // 调用Service层更新数据集元数据和文件
            boolean result = datasetService.updateDataset(id, name, description, status, file);
            return Result.success(result);
        } catch (Exception e) {
            return Result.error(500, "更新数据集失败: " + e.getMessage());
        }
    }
}