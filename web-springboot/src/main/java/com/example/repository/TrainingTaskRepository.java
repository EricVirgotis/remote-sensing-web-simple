package com.example.repository;

import com.example.entity.TrainingTask;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TrainingTaskRepository extends JpaRepository<TrainingTask, Long> {
    List<TrainingTask> findByUserId(Long userId);
}