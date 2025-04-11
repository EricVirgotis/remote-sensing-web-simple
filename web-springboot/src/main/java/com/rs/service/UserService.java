package com.rs.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.rs.dto.UserInfoDTO;
import com.rs.dto.UserLoginDTO;
import com.rs.dto.UserRegisterDTO;
import com.rs.entity.User;

/**
 * 用户服务接口
 */
public interface UserService extends IService<User> {
    
    /**
     * 用户注册
     *
     * @param registerDTO 注册信息
     * @return 用户ID
     */
    Long register(UserRegisterDTO registerDTO);
    
    /**
     * 用户登录
     *
     * @param loginDTO 登录信息
     * @return 登录token
     */
    String login(UserLoginDTO loginDTO);
    
    /**
     * 获取用户信息
     *
     * @param userId 用户ID
     * @return 用户信息
     */
    UserInfoDTO getUserInfo(Long userId);
    
    /**
     * 更新用户信息
     *
     * @param userId 用户ID
     * @param userInfoDTO 用户信息
     * @return 是否成功
     */
    boolean updateUserInfo(Long userId, UserInfoDTO userInfoDTO);
    
    /**
     * 分页查询用户列表
     *
     * @param page 分页参数
     * @param username 用户名
     * @param status 状态
     * @return 用户列表
     */
    Page<User> getUserPage(Page<User> page, String username, Integer status);
    
    /**
     * 修改用户状态
     *
     * @param userId 用户ID
     * @param status 状态
     * @return 是否成功
     */
    boolean updateUserStatus(Long userId, Integer status);
    
    /**
     * 重置用户密码
     *
     * @param userId 用户ID
     * @param newPassword 新密码
     * @return 是否成功
     */
    boolean resetPassword(Long userId, String newPassword);
    
    /**
     * 用户登出
     *
     * @return 是否成功
     */
    boolean logout();
}