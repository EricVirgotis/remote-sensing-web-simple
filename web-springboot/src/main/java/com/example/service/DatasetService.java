package com.example.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.example.entity.Dataset;
import org.springframework.web.multipart.MultipartFile;

/**
 * 数据集服务接口
 */
public interface DatasetService extends IService<Dataset> {
    
    /**
     * 上传数据集
     *
     * @param userId 用户ID
     * @param file 数据集文件
     * @param name 数据集名称
     * @param description 数据集描述
     * @return 数据集ID
     */
    Long uploadDataset(Long userId, MultipartFile file, String name, String description);
    
    /**
     * 分页查询数据集
     *
     * @param page 分页参数
     * @param name 数据集名称
     * @param status 状态
     * @return 分页结果
     */
    Page<Dataset> pageDatasets(Page<Dataset> page, String name, Integer status);
    
    /**
     * 获取数据集详情
     *
     * @param id 数据集ID
     * @return 数据集信息
     */
    Dataset getDatasetDetail(Long id);
    
    /**
     * 删除数据集
     *
     * @param id 数据集ID
     * @return 是否成功
     */
    boolean deleteDataset(Long id);
    
    /**
     * 获取数据集文件路径
     *
     * @param id 数据集ID
     * @return 文件路径
     */
    String getDatasetPath(Long id);
    
    /**
     * 更新数据集
     *
     * @param id 数据集ID
     * @param name 数据集名称
     * @param description 数据集描述
     * @param status 状态
     * @param file 数据集文件（可选）
     * @return 是否成功
     */
    boolean updateDataset(Long id, String name, String description, Integer status, MultipartFile file);
    
    /**
     * 创建数据集
     *
     * @param dataset 数据集对象
     * @param file 数据集文件（可选）
     * @return 创建的数据集
     */
    Dataset createDataset(Dataset dataset, MultipartFile file);
}