package com.rs.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.rs.common.Result;
import com.rs.dto.RemoteImageUploadDTO;
import com.rs.entity.RemoteImage;
import com.rs.service.RemoteImageService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

/**
 * 遥感影像控制器
 */
@Tag(name = "遥感影像管理", description = "遥感影像相关接口")
@RestController
@RequestMapping("/api/images")
public class RemoteImageController {

    @Autowired
    private RemoteImageService remoteImageService;

    @Operation(summary = "上传遥感影像")
    @PostMapping
    public Result<Long> uploadImage(
            @Parameter(description = "用户ID") @RequestHeader("X-User-ID") Long userId,
            @Parameter(description = "影像文件") @RequestParam("file") MultipartFile file,
            @Parameter(description = "上传信息") RemoteImageUploadDTO uploadDTO) {
        return Result.success(remoteImageService.uploadImage(userId, file, uploadDTO));
    }

    @Operation(summary = "获取影像详情")
    @GetMapping("/{imageId}")
    public Result<RemoteImage> getImageDetail(
            @Parameter(description = "影像ID") @PathVariable Long imageId) {
        return Result.success(remoteImageService.getImageDetail(imageId));
    }

    @Operation(summary = "分页查询用户的影像列表")
    @GetMapping("/page")
    public Result<Page<RemoteImage>> getUserImagePage(
            @Parameter(description = "用户ID") @RequestHeader("X-User-ID") Long userId,
            @Parameter(description = "页码") @RequestParam(defaultValue = "1") Integer current,
            @Parameter(description = "每页条数") @RequestParam(defaultValue = "10") Integer size,
            @Parameter(description = "影像名称") @RequestParam(required = false) String imageName) {
        Page<RemoteImage> page = new Page<>(current, size);
        return Result.success(remoteImageService.getUserImagePage(page, userId, imageName));
    }

    @Operation(summary = "删除影像")
    @DeleteMapping("/{imageId}")
    public Result<Boolean> deleteImage(
            @Parameter(description = "用户ID") @RequestHeader("X-User-ID") Long userId,
            @Parameter(description = "影像ID") @PathVariable Long imageId) {
        return Result.success(remoteImageService.deleteImage(userId, imageId));
    }
}