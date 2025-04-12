package com.example.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.rs.common.Result;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Collections;
import jakarta.servlet.http.HttpServletResponse;

@RestController
@RequestMapping("/dataset")
public class DatasetController {
    
    @PostMapping
    public Integer createDataset(@RequestParam("file") MultipartFile file) {
        try {
            // 保存文件到临时目录
            String tempDir = System.getProperty("java.io.tmpdir");
            File dest = new File(tempDir + File.separator + file.getOriginalFilename());
            file.transferTo(dest);
            
            // 这里应该调用服务层处理数据集创建逻辑
            // 返回数据集ID
            return 1;
        } catch (IOException e) {
            throw new RuntimeException("文件上传失败", e);
        }
    }
    
    @GetMapping("/list_datasets")
    public Object pageDatasets(
        @RequestParam Integer current,
        @RequestParam Integer size,
        @RequestParam(required = false) String name,
        @RequestParam(required = false) Integer status
    ) {
        Page<Object> page = new Page<>(current, size);
        // 这里应该调用Mapper或Service层进行分页查询
        // 示例: return datasetService.pageDatasets(page, name, status);
        return new HashMap<String, Object>() {{
            put("records", Collections.emptyList());
            put("total", 0);
            put("size", size);
            put("current", current);
        }};
    }
    
    @GetMapping("/{id}")
    public Object getDatasetDetail(@PathVariable Integer id) {
        // 这里应该调用Mapper或Service层查询数据集详情
        // 示例: return datasetService.getDatasetDetail(id);
        return new HashMap<String, Object>() {{
            put("id", id);
            put("name", "示例数据集");
            put("status", 1);
            put("createTime", "2023-01-01");
        }};
    }
    
    @DeleteMapping("/{id}")
    public Result<Boolean> deleteDataset(@PathVariable Integer id) {
        try {
            // 这里应该调用Service层删除数据集
            // 示例: return Result.success(datasetService.deleteDataset(id));
            return Result.success(true);
        } catch (Exception e) {
            return Result.error(500, "删除数据集失败: " + e.getMessage());
        }
    }
    
    private String getDatasetFilePath(Integer id) {
        // 这里应该实现根据ID获取数据集文件路径的逻辑
        // 示例: return datasetService.getDatasetPath(id);
        return System.getProperty("java.io.tmpdir") + File.separator + "dataset_" + id + ".zip";
    }
    
    @GetMapping("/{id}/download")
    public void downloadDataset(@PathVariable Integer id, HttpServletResponse response) throws IOException {
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
        @PathVariable Integer id,
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
            
            // 处理文件更新
            if (file != null && !file.isEmpty()) {
                String tempDir = System.getProperty("java.io.tmpdir");
                File dest = new File(tempDir + File.separator + "dataset_" + id + ".zip");
                file.transferTo(dest);
            }
            
            // 这里应该调用Service层更新数据集元数据和文件
            // 示例: return Result.success(datasetService.updateDataset(id, name, description, status, file));
            return Result.success(true);
        } catch (IOException e) {
            return Result.error(500, "文件上传失败: " + e.getMessage());
        } catch (Exception e) {
            return Result.error(500, "更新数据集失败: " + e.getMessage());
        }
    }
}