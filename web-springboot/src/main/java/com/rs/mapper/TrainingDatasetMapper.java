package com.rs.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.rs.entity.TrainingDataset;
import org.apache.ibatis.annotations.Mapper;


/**
 * 训练数据集Mapper接口
 */
@Mapper
public interface TrainingDatasetMapper extends BaseMapper<TrainingDataset> {
    
}