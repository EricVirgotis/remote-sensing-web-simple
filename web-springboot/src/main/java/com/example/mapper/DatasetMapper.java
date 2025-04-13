package com.example.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.entity.Dataset;
import org.apache.ibatis.annotations.Mapper;

/**
 * 数据集Mapper接口
 */
@Mapper
public interface DatasetMapper extends BaseMapper<Dataset> {
    
}