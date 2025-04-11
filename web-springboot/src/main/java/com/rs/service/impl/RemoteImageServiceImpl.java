package com.rs.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rs.dto.RemoteImageUploadDTO;
import com.rs.entity.RemoteImage;
import com.rs.exception.BusinessException;
import com.rs.mapper.RemoteImageMapper;
import com.rs.service.RemoteImageService;
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
 * 遥感影像服务实现类
 */
@Slf4j
@Service
public class RemoteImageServiceImpl extends ServiceImpl<RemoteImageMapper, RemoteImage> implements RemoteImageService {

    @Value("${rs.file-storage.remote-image-path}")
    private String remoteImagePath;
    
    // 支持的影像格式
    private static final List<String> SUPPORTED_FORMATS = Arrays.asList(
            "tif", "tiff", "img", "jpg", "jpeg", "png", "bmp", "gif"
    );

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Long uploadImage(Long userId, MultipartFile file, RemoteImageUploadDTO uploadDTO) {
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
            
            // 创建影像记录
            RemoteImage remoteImage = new RemoteImage();
            remoteImage.setUserId(userId);
            remoteImage.setImageName(uploadDTO.getImageName() != null ? uploadDTO.getImageName() : originalFilename);
            remoteImage.setImagePath(storagePath);
            remoteImage.setImageSize(file.getSize());
            remoteImage.setImageFormat(fileExtension);
            remoteImage.setUploadTime(LocalDateTime.now());
            remoteImage.setDescription(uploadDTO.getDescription());
            remoteImage.setStatus(1); // 有效状态
            remoteImage.setCreateTime(LocalDateTime.now());
            remoteImage.setUpdateTime(LocalDateTime.now());
            
            // 保存记录
            this.save(remoteImage);
            
            return remoteImage.getId();
        } catch (IOException e) {
            log.error("保存遥感影像文件失败", e);
            throw new BusinessException("保存遥感影像文件失败");
        }
    }

    @Override
    public RemoteImage getImageDetail(Long imageId) {
        RemoteImage remoteImage = this.getById(imageId);
        if (remoteImage == null) {
            throw new BusinessException("影像不存在");
        }
        return remoteImage;
    }

    @Override
    public Page<RemoteImage> getUserImagePage(Page<RemoteImage> page, Long userId, String imageName) {
        LambdaQueryWrapper<RemoteImage> queryWrapper = new LambdaQueryWrapper<>();
        // 添加查询条件
        queryWrapper.eq(RemoteImage::getUserId, userId);
        queryWrapper.like(imageName != null, RemoteImage::getImageName, imageName);
        queryWrapper.eq(RemoteImage::getStatus, 1); // 有效状态
        // 按上传时间降序排序
        queryWrapper.orderByDesc(RemoteImage::getUploadTime);
        
        return this.page(page, queryWrapper);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean deleteImage(Long userId, Long imageId) {
        // 查询影像
        RemoteImage remoteImage = this.getById(imageId);
        if (remoteImage == null) {
            throw new BusinessException("影像不存在");
        }
        
        // 检查权限
        if (!remoteImage.getUserId().equals(userId)) {
            throw new BusinessException("无权操作此影像");
        }
        
        // 逻辑删除影像记录
        remoteImage.setStatus(0); // 无效状态
        remoteImage.setUpdateTime(LocalDateTime.now());
        
        // 物理删除文件（可选，也可以只做逻辑删除）
        try {
            Path filePath = Paths.get(remoteImage.getImagePath());
            if (Files.exists(filePath)) {
                Files.delete(filePath);
            }
        } catch (IOException e) {
            log.error("删除遥感影像文件失败", e);
            // 继续执行，至少完成数据库的逻辑删除
        }
        
        return this.updateById(remoteImage);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateImageInfo(Long userId, Long imageId, String imageName, String description) {
        // 查询影像
        RemoteImage remoteImage = this.getById(imageId);
        if (remoteImage == null) {
            throw new BusinessException("影像不存在");
        }
        
        // 检查权限
        if (!remoteImage.getUserId().equals(userId)) {
            throw new BusinessException("无权操作此影像");
        }
        
        // 更新信息
        if (imageName != null && !imageName.isEmpty()) {
            remoteImage.setImageName(imageName);
        }
        remoteImage.setDescription(description);
        remoteImage.setUpdateTime(LocalDateTime.now());
        
        return this.updateById(remoteImage);
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
        
        return remoteImagePath + File.separator + 
               userId + File.separator + 
               dateDir + File.separator + 
               filename;
    }
}