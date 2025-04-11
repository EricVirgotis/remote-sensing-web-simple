package com.rs.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.rs.entity.TrainingTask;
import org.apache.ibatis.annotations.Mapper;

/**
 * 模型训练任务Mapper接口
 */
@Mapper
public interface TrainingTaskMapper extends BaseMapper<TrainingTask> {
    
}