package com.example.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.entity.Dataset;
import com.example.mapper.DatasetMapper;
import com.example.service.DatasetService;
import com.rs.exception.BusinessException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.List;

/**
 * 数据集服务实现类
 */
@Slf4j
@Service
public class DatasetServiceImpl extends ServiceImpl<DatasetMapper, Dataset> implements DatasetService {

    @Value("${rs.file-storage.base-path}")
    private String baseStoragePath;
    
    // 支持的数据集文件格式
    private static final List<String> SUPPORTED_FORMATS = Arrays.asList(
            "zip", "rar", "tar", "gz", "7z"
    );

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Long uploadDataset(Long userId, MultipartFile file, String name, String description) {
        // 检查文件是否为空
        if (file == null || file.isEmpty()) {
            throw new BusinessException("上传文件不能为空");
        }
        
        // 获取文件信息
        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null || originalFilename.isEmpty()) {
            throw new BusinessException("文件名不能为空");
        }
        
        // 检查文件格式
        String fileExtension = getFileExtension(originalFilename).toLowerCase();
        if (!SUPPORTED_FORMATS.contains(fileExtension)) {
            throw new BusinessException("不支持的文件格式，仅支持：" + String.join(", ", SUPPORTED_FORMATS));
        }
        
        // 生成存储路径
        String storagePath = generateStoragePath(userId, fileExtension);
        File targetFile = new File(storagePath);
        
        // 确保目录存在
        File parentDir = targetFile.getParentFile();
        if (!parentDir.exists() && !parentDir.mkdirs()) {
            throw new BusinessException("创建存储目录失败");
        }
        
        try {
            // 保存文件
            file.transferTo(targetFile);
            
            // 创建数据集记录
            Dataset dataset = new Dataset();
            dataset.setUserId(userId);
            dataset.setName(name != null && !name.isEmpty() ? name : originalFilename);
            dataset.setFilePath(storagePath);
            dataset.setFileSize(file.getSize());
            dataset.setDescription(description);
            dataset.setStatus(1); // 有效状态
            dataset.setCreateTime(LocalDateTime.now());
            dataset.setUpdateTime(LocalDateTime.now());
            dataset.setDeleted(0); // 未删除
            
            // 保存记录
            this.save(dataset);
            
            return dataset.getId();
        } catch (IOException e) {
            log.error("保存数据集文件失败", e);
            throw new BusinessException("保存数据集文件失败");
        }
    }

    @Override
    public Page<Dataset> pageDatasets(Page<Dataset> page, String name, Integer status) {
        LambdaQueryWrapper<Dataset> queryWrapper = new LambdaQueryWrapper<>();
        // 添加查询条件
        queryWrapper.like(name != null, Dataset::getName, name);
        queryWrapper.eq(status != null, Dataset::getStatus, status);
        // 按创建时间降序排序
        queryWrapper.orderByDesc(Dataset::getCreateTime);
        
        return this.page(page, queryWrapper);
    }

    @Override
    public Dataset getDatasetDetail(Long id) {
        Dataset dataset = this.getById(id);
        if (dataset == null) {
            throw new BusinessException("数据集不存在");
        }
        return dataset;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean deleteDataset(Long id) {
        // 查询数据集
        Dataset dataset = this.getById(id);
        if (dataset == null) {
            throw new BusinessException("数据集不存在");
        }
        
        // 检查数据集文件是否存在
        File datasetFile = new File(dataset.getFilePath());
        if (!datasetFile.exists()) {
            // 文件不存在则直接删除数据库记录
            return this.removeById(id);
        }
        
        // 逻辑删除数据集记录
        dataset.setStatus(0); // 无效状态
        dataset.setUpdateTime(LocalDateTime.now());
        
        // 物理删除文件（可选，也可以只做逻辑删除）
        try {
            Path filePath = Paths.get(dataset.getFilePath());
            if (Files.exists(filePath)) {
                Files.delete(filePath);
            }
        } catch (IOException e) {
            log.error("删除数据集文件失败", e);
            // 继续执行，至少完成数据库的逻辑删除
        }
        
        return this.updateById(dataset);
    }

    @Override
    public String getDatasetPath(Long id) {
        Dataset dataset = this.getById(id);
        if (dataset == null) {
            throw new BusinessException("数据集不存在");
        }
        return dataset.getFilePath();
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Dataset createDataset(Dataset dataset, MultipartFile file) {
        // 处理文件上传
        if (file != null && !file.isEmpty()) {
            // 获取文件信息
            String originalFilename = file.getOriginalFilename();
            if (originalFilename == null || originalFilename.isEmpty()) {
                throw new BusinessException("文件名不能为空");
            }
            
            // 检查文件格式
            String fileExtension = getFileExtension(originalFilename).toLowerCase();
            if (!SUPPORTED_FORMATS.contains(fileExtension)) {
                throw new BusinessException("不支持的文件格式，仅支持：" + String.join(", ", SUPPORTED_FORMATS));
            }
            
            // 生成存储路径
            String storagePath = generateStoragePath(dataset.getUserId(), fileExtension);
            File targetFile = new File(storagePath);
            
            // 确保目录存在
            File parentDir = targetFile.getParentFile();
            if (!parentDir.exists() && !parentDir.mkdirs()) {
                throw new BusinessException("创建存储目录失败");
            }
            
            try {
                // 保存文件
                file.transferTo(targetFile);
                
                // 更新数据集文件信息
                dataset.setFilePath(storagePath);
                dataset.setFileSize(file.getSize());
            } catch (IOException e) {
                log.error("保存数据集文件失败", e);
                throw new BusinessException("保存数据集文件失败");
            }
        }
        
        // 设置数据集基本信息
        dataset.setStatus(1); // 有效状态
        dataset.setCreateTime(LocalDateTime.now());
        dataset.setUpdateTime(LocalDateTime.now());
        dataset.setDeleted(0); // 未删除
        
        // 保存记录
        this.save(dataset);
        return dataset;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateDataset(Long id, String name, String description, Integer status, MultipartFile file) {
        // 查询数据集
        Dataset dataset = this.getById(id);
        if (dataset == null) {
            throw new BusinessException("数据集不存在");
        }
        
        // 更新信息
        if (name != null && !name.isEmpty()) {
            dataset.setName(name);
        }
        dataset.setDescription(description);
        if (status != null) {
            dataset.setStatus(status);
        }
        dataset.setUpdateTime(LocalDateTime.now());
        
        // 处理文件更新
        if (file != null && !file.isEmpty()) {
            try {
                // 获取文件信息
                String originalFilename = file.getOriginalFilename();
                if (originalFilename == null || originalFilename.isEmpty()) {
                    throw new BusinessException("文件名不能为空");
                }
                
                // 检查文件格式
                String fileExtension = getFileExtension(originalFilename).toLowerCase();
                if (!SUPPORTED_FORMATS.contains(fileExtension)) {
                    throw new BusinessException("不支持的文件格式，仅支持：" + String.join(", ", SUPPORTED_FORMATS));
                }
                
                // 删除旧文件
                Path oldFilePath = Paths.get(dataset.getFilePath());
                if (Files.exists(oldFilePath)) {
                    Files.delete(oldFilePath);
                }
                
                // 生成新的存储路径
                String storagePath = generateStoragePath(dataset.getUserId(), fileExtension);
                File targetFile = new File(storagePath);
                
                // 确保目录存在
                File parentDir = targetFile.getParentFile();
                if (!parentDir.exists() && !parentDir.mkdirs()) {
                    throw new BusinessException("创建存储目录失败");
                }
                
                // 保存文件
                file.transferTo(targetFile);
                
                // 更新文件信息
                dataset.setFilePath(storagePath);
                dataset.setFileSize(file.getSize());
            } catch (IOException e) {
                log.error("更新数据集文件失败", e);
                throw new BusinessException("更新数据集文件失败");
            }
        }
        
        return this.updateById(dataset);
    }
    
    /**
     * 获取文件扩展名
     *
     * @param filename 文件名
     * @return 扩展名
     */
    private String getFileExtension(String filename) {
        int dotIndex = filename.lastIndexOf('.');
        return (dotIndex == -1) ? "" : filename.substring(dotIndex + 1);
    }
    
    /**
     * 生成存储路径
     *
     * @param userId 用户ID
     * @param fileExtension 文件扩展名
     * @return 存储路径
     */
    private String generateStoragePath(Long userId, String fileExtension) {
        // 按日期和用户ID组织目录结构
        String dateDir = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String filename = System.currentTimeMillis() + "." + fileExtension;
        
        return baseStoragePath + File.separator + "dataset" + File.separator + 
               dateDir + File.separator + userId + File.separator + filename;
    }
}