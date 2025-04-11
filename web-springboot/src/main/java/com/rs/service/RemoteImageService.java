package com.rs.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.rs.dto.RemoteImageUploadDTO;
import com.rs.entity.RemoteImage;
import org.springframework.web.multipart.MultipartFile;

/**
 * 遥感影像服务接口
 */
public interface RemoteImageService extends IService<RemoteImage> {
    
    /**
     * 上传遥感影像
     *
     * @param userId 用户ID
     * @param file 影像文件
     * @param uploadDTO 上传信息
     * @return 影像ID
     */
    Long uploadImage(Long userId, MultipartFile file, RemoteImageUploadDTO uploadDTO);
    
    /**
     * 获取影像详情
     *
     * @param imageId 影像ID
     * @return 影像信息
     */
    RemoteImage getImageDetail(Long imageId);
    
    /**
     * 分页查询用户的影像列表
     *
     * @param page 分页参数
     * @param userId 用户ID
     * @param imageName 影像名称
     * @return 影像列表
     */
    Page<RemoteImage> getUserImagePage(Page<RemoteImage> page, Long userId, String imageName);
    
    /**
     * 删除影像
     *
     * @param userId 用户ID
     * @param imageId 影像ID
     * @return 是否成功
     */
    boolean deleteImage(Long userId, Long imageId);
    
    /**
     * 更新影像信息
     *
     * @param userId 用户ID
     * @param imageId 影像ID
     * @param imageName 影像名称
     * @param description 影像描述
     * @return 是否成功
     */
    boolean updateImageInfo(Long userId, Long imageId, String imageName, String description);
}